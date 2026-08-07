"""Business logic chọn universe coin. File này kiểm tra symbol, Spot USDT, stablecoin pair, leveraged token và quote volume."""

from dataclasses import dataclass, field
from typing import Protocol

from finsight.config.constants import (
    CANDIDATE_SYMBOLS,
    LEVERAGED_TOKEN_MARKERS,
    REQUIRED_SYMBOLS,
    STABLECOIN_ASSETS,
)
from finsight.config.time import utc_now
from finsight.crawl.binance.schemas import BinanceSymbolInfo, BinanceTicker24hr


class BinanceUniverseProvider(Protocol):
    async def exchange_info(self, symbol: str | None = None) -> dict: ...

    async def ticker_24hr(self, symbol: str | None = None) -> list[dict]: ...


@dataclass(frozen=True)
class SymbolDecision:
    symbol: str
    accepted: bool
    reasons: tuple[str, ...] = ()
    quote_volume: float = 0.0
    source: str = "ranked"


@dataclass(frozen=True)
class UniverseBuildResult:
    universe_name: str
    version: str
    quote_asset: str
    min_symbols: int
    max_symbols: int
    selected_symbols: tuple[str, ...]
    decisions: tuple[SymbolDecision, ...]
    generated_at: str
    selection_config: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "universe_name": self.universe_name,
            "version": self.version,
            "quote_asset": self.quote_asset,
            "min_symbols": self.min_symbols,
            "max_symbols": self.max_symbols,
            "selected_symbols": list(self.selected_symbols),
            "decisions": [
                {
                    "symbol": decision.symbol,
                    "accepted": decision.accepted,
                    "reasons": list(decision.reasons),
                    "quote_volume": decision.quote_volume,
                    "source": decision.source,
                }
                for decision in self.decisions
            ],
            "generated_at": self.generated_at,
            "selection_config": self.selection_config,
        }


class UniverseBuilder:
    def __init__(
        self,
        provider: BinanceUniverseProvider,
        required_symbols: tuple[str, ...] = REQUIRED_SYMBOLS,
        candidate_symbols: tuple[str, ...] = CANDIDATE_SYMBOLS,
        min_quote_volume: float = 10_000_000,
    ) -> None:
        self.provider = provider
        self.required_symbols = tuple(symbol.upper() for symbol in required_symbols)
        self.candidate_symbols = tuple(symbol.upper() for symbol in candidate_symbols)
        self.min_quote_volume = min_quote_volume

    async def build(
        self,
        quote_asset: str = "USDT",
        limit: int = 10,
        min_symbols: int = 8,
        universe_name: str = "crypto_spot_usdt_v1",
    ) -> UniverseBuildResult:
        if limit < min_symbols:
            raise ValueError("limit must be greater than or equal to min_symbols")

        quote_asset = quote_asset.upper()
        exchange_info_payload, ticker_payload = await self._fetch_market_snapshot()
        symbols = self._parse_symbols(exchange_info_payload)
        tickers = self._parse_tickers(ticker_payload)

        selected: list[str] = []
        decisions: dict[str, SymbolDecision] = {}

        priority_symbols = [*self.required_symbols, *self.candidate_symbols]
        for symbol in priority_symbols:
            if symbol in decisions:
                continue
            decision = self._decide_symbol(
                symbol=symbol,
                symbol_info=symbols.get(symbol),
                ticker=tickers.get(symbol),
                quote_asset=quote_asset,
                source="required" if symbol in self.required_symbols else "candidate",
            )
            decisions[symbol] = decision
            if decision.accepted and len(selected) < limit:
                selected.append(symbol)

        if len(selected) < limit:
            ranked_symbols = sorted(
                (
                    symbol
                    for symbol, info in symbols.items()
                    if info.quote_asset == quote_asset and symbol not in decisions
                ),
                key=lambda symbol: tickers.get(symbol, BinanceTicker24hr(symbol=symbol)).quote_volume,
                reverse=True,
            )
            for symbol in ranked_symbols:
                if len(selected) >= limit:
                    break
                decision = self._decide_symbol(
                    symbol=symbol,
                    symbol_info=symbols.get(symbol),
                    ticker=tickers.get(symbol),
                    quote_asset=quote_asset,
                    source="ranked_by_quote_volume",
                )
                decisions[symbol] = decision
                if decision.accepted:
                    selected.append(symbol)

        result_version = utc_now().strftime("%Y%m%dT%H%M%SZ")
        return UniverseBuildResult(
            universe_name=universe_name,
            version=result_version,
            quote_asset=quote_asset,
            min_symbols=min_symbols,
            max_symbols=limit,
            selected_symbols=tuple(selected),
            decisions=tuple(decisions.values()),
            generated_at=utc_now().isoformat(),
            selection_config={
                "required_symbols": list(self.required_symbols),
                "candidate_symbols": list(self.candidate_symbols),
                "min_quote_volume": self.min_quote_volume,
            },
        )

    async def _fetch_market_snapshot(self) -> tuple[dict, list[dict]]:
        exchange_info_payload = await self.provider.exchange_info()
        ticker_payload = await self.provider.ticker_24hr()
        return exchange_info_payload, ticker_payload

    def _parse_symbols(self, payload: dict) -> dict[str, BinanceSymbolInfo]:
        return {
            item["symbol"]: BinanceSymbolInfo.model_validate(item)
            for item in payload.get("symbols", [])
            if "symbol" in item
        }

    def _parse_tickers(self, payload: list[dict]) -> dict[str, BinanceTicker24hr]:
        return {
            item["symbol"]: BinanceTicker24hr.model_validate(item)
            for item in payload
            if "symbol" in item
        }

    def _decide_symbol(
        self,
        symbol: str,
        symbol_info: BinanceSymbolInfo | None,
        ticker: BinanceTicker24hr | None,
        quote_asset: str,
        source: str,
    ) -> SymbolDecision:
        reasons: list[str] = []

        if symbol_info is None:
            return SymbolDecision(symbol=symbol, accepted=False, reasons=("missing_exchange_info",), source=source)

        if symbol_info.status != "TRADING":
            reasons.append("status_not_trading")
        if symbol_info.quote_asset != quote_asset:
            reasons.append("quote_asset_mismatch")
        if not symbol_info.is_spot_trading_allowed:
            reasons.append("spot_trading_not_allowed")
        if self._is_stablecoin_pair(symbol_info):
            reasons.append("stablecoin_pair")
        if self._is_leveraged_token(symbol_info.base_asset):
            reasons.append("leveraged_token")

        quote_volume = ticker.quote_volume if ticker else 0.0
        if ticker is None:
            reasons.append("missing_24hr_ticker")
        elif quote_volume < self.min_quote_volume:
            reasons.append("quote_volume_below_minimum")

        return SymbolDecision(
            symbol=symbol,
            accepted=not reasons,
            reasons=tuple(reasons),
            quote_volume=quote_volume,
            source=source,
        )

    def _is_stablecoin_pair(self, symbol_info: BinanceSymbolInfo) -> bool:
        return symbol_info.base_asset in STABLECOIN_ASSETS and symbol_info.quote_asset in STABLECOIN_ASSETS

    def _is_leveraged_token(self, base_asset: str) -> bool:
        return any(base_asset.endswith(marker) for marker in LEVERAGED_TOKEN_MARKERS)

