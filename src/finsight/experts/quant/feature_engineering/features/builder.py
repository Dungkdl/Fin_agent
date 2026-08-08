"""Lớp orchestrator để tính toán toàn bộ các Feature."""

import pandas as pd

from finsight.experts.quant.feature_engineering.features.price import add_price_features
from finsight.experts.quant.feature_engineering.features.volatility import add_volatility_features
from finsight.experts.quant.feature_engineering.features.momentum import add_momentum_features
from finsight.experts.quant.feature_engineering.features.volume import add_volume_features
from finsight.experts.quant.feature_engineering.features.time_features import add_time_features
from finsight.experts.quant.feature_engineering.features.regime import add_regime_features
from finsight.experts.quant.feature_engineering.features.cross_asset import add_cross_asset_features


class SharedFeatureBuilder:
    def __init__(self, config: dict):
        """
        config map từ file yaml (phần features:)
        VD: {"include_price": True, "include_volatility": True, ...}
        """
        self.config = config

    def build_core_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tính các feature cơ bản không phụ thuộc vào cross-asset context.
        Dùng cho cả offline bulk train và realtime inference.
        """
        if len(df) == 0:
            return df
            
        if self.config.get("include_price", True):
            df = add_price_features(df)
            
        if self.config.get("include_volatility", True):
            df = add_volatility_features(df)
            
        if self.config.get("include_momentum", True):
            df = add_momentum_features(df)
            
        if self.config.get("include_volume", True):
            df = add_volume_features(df)
            
        if self.config.get("include_time", True):
            df = add_time_features(df)
            
        if self.config.get("include_regime", True):
            df = add_regime_features(df)
            
        return df

    def build_cross_features(self, df: pd.DataFrame, context_dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Tính các feature phụ thuộc vào bối cảnh thị trường (BTC/ETH).
        """
        if len(df) == 0:
            return df
            
        if self.config.get("include_cross_asset", True):
            df = add_cross_asset_features(df, context_dfs)
            
        return df
