from typing import Literal, TypedDict

import pandas as pd

SignalName = Literal["BUY", "SELL", "NEUTRAL"]


class Pivot(TypedDict):
    index: int
    kind: Literal["high", "low"]
    value: float


class Zone(TypedDict):
    kind: Literal["high", "low"]
    center: float
    touches: int
    first_index: int
    last_index: int


class SupportResistanceResult(TypedDict):
    signal: SignalName
    status: str
    support: float | None
    resistance: float | None
    value: float | None
    price_series: list[float]


def _empty_result() -> SupportResistanceResult:
    return {
        "signal": "NEUTRAL",
        "status": "RANGE",
        "support": None,
        "resistance": None,
        "value": None,
        "price_series": [],
    }


def _collect_pivots(source_frame: pd.DataFrame, swing_window: int) -> list[Pivot]:
    pivots: list[Pivot] = []
    highs = source_frame["high"].tolist()
    lows = source_frame["low"].tolist()

    for index in range(swing_window, len(source_frame) - swing_window):
        high_value = highs[index]
        low_value = lows[index]
        left_highs = highs[index - swing_window : index]
        right_highs = highs[index + 1 : index + swing_window + 1]
        left_lows = lows[index - swing_window : index]
        right_lows = lows[index + 1 : index + swing_window + 1]

        if all(high_value >= item for item in left_highs + right_highs):
            pivots.append({"index": index, "kind": "high", "value": float(high_value)})

        if all(low_value <= item for item in left_lows + right_lows):
            pivots.append({"index": index, "kind": "low", "value": float(low_value)})

    pivots.sort(key=lambda item: item["index"])
    return pivots


def _cluster_zones(pivots: list[Pivot], threshold: float) -> list[Zone]:
    zones: list[Zone] = []

    for pivot in pivots:
        matching_zone = next(
            (
                zone
                for zone in zones
                if zone["kind"] == pivot["kind"] and abs(zone["center"] - pivot["value"]) <= threshold
            ),
            None,
        )

        if matching_zone is None:
            zones.append(
                {
                    "kind": pivot["kind"],
                    "center": pivot["value"],
                    "touches": 1,
                    "first_index": pivot["index"],
                    "last_index": pivot["index"],
                }
            )
            continue

        total_touches = matching_zone["touches"] + 1
        matching_zone["center"] = (matching_zone["center"] * matching_zone["touches"] + pivot["value"]) / total_touches
        matching_zone["touches"] = total_touches
        matching_zone["first_index"] = min(matching_zone["first_index"], pivot["index"])
        matching_zone["last_index"] = max(matching_zone["last_index"], pivot["index"])

    return zones


def _pick_best_zone(
    zones: list[Zone],
    *,
    kind: Literal["high", "low"],
    latest_close: float,
    latest_index: int,
    full_range: float,
) -> float | None:
    filtered = [
        zone
        for zone in zones
        if zone["kind"] == kind and ((zone["center"] >= latest_close) if kind == "high" else (zone["center"] <= latest_close))
    ]
    if not filtered:
        return None

    distance_scale = max(full_range * 0.35, 1e-9)

    def zone_score(zone: Zone) -> float:
        distance = abs(zone["center"] - latest_close)
        recency = max(latest_index - zone["last_index"], 0)
        span = max(zone["last_index"] - zone["first_index"], 0)

        return (
            zone["touches"] * 3.0
            + min(span / max(latest_index, 1), 1.0) * 1.5
            + max(0.0, 1.0 - (distance / distance_scale)) * 2.5
            + max(0.0, 1.0 - (recency / max(latest_index, 1))) * 1.75
        )

    best_zone = max(
        filtered,
        key=lambda zone: (
            zone_score(zone),
            zone["touches"],
            zone["last_index"],
            -abs(zone["center"] - latest_close),
        ),
    )
    return float(best_zone["center"])


def _fallback_level(source_frame: pd.DataFrame, *, kind: Literal["high", "low"]) -> float:
    recent_window = source_frame.tail(30)
    if kind == "low":
        return float(recent_window["low"].quantile(0.2))

    return float(recent_window["high"].quantile(0.8))


def calc_support_resistance(dataframe: pd.DataFrame, *, swing_window: int = 2) -> SupportResistanceResult:
    required_columns = {"high", "low", "close"}
    if dataframe.empty or not required_columns.issubset(dataframe.columns):
        return _empty_result()

    source_frame = dataframe.tail(96).reset_index(drop=True)
    latest_close = float(source_frame["close"].iloc[-1])
    latest_index = len(source_frame) - 1
    recent_closes = source_frame["close"].tail(8).tolist()
    previous_close = float(recent_closes[0]) if recent_closes else latest_close
    slope = latest_close - previous_close
    effective_swing_window = max(swing_window, 3)
    pivots = _collect_pivots(source_frame, swing_window=effective_swing_window)
    full_range = float(source_frame["high"].max() - source_frame["low"].min())
    median_bar_range = float((source_frame["high"] - source_frame["low"]).tail(48).median())
    zone_threshold = max(full_range * 0.01, median_bar_range * 1.35, 1e-9)
    zones = _cluster_zones(pivots, zone_threshold)
    support = _pick_best_zone(
        zones,
        kind="low",
        latest_close=latest_close,
        latest_index=latest_index,
        full_range=full_range,
    )
    resistance = _pick_best_zone(
        zones,
        kind="high",
        latest_close=latest_close,
        latest_index=latest_index,
        full_range=full_range,
    )

    if support is None:
        support = _fallback_level(source_frame, kind="low")

    if resistance is None:
        resistance = _fallback_level(source_frame, kind="high")

    range_value = max(resistance - support, 1e-9)
    support_distance = abs(latest_close - support)
    resistance_distance = abs(latest_close - resistance)
    support_proximity = support_distance / range_value
    resistance_proximity = resistance_distance / range_value
    price_position = (latest_close - support) / range_value
    threshold = 0.16
    slope_threshold = max(median_bar_range * 0.2, range_value * 0.015, 1e-9)

    signal: SignalName = "NEUTRAL"
    status = "RANGE"

    if support_proximity <= threshold and slope >= -slope_threshold:
        signal = "BUY"
        status = "DEFENDEU_SUPORTE"
    elif resistance_proximity <= threshold and slope <= slope_threshold:
        signal = "SELL"
        status = "REJEITOU_RESISTENCIA"
    elif price_position >= 0.62 and resistance_proximity <= 0.34 and slope > slope_threshold:
        signal = "SELL"
        status = "PRESSIONANDO_RESISTENCIA"
    elif price_position <= 0.38 and support_proximity <= 0.34 and slope < -slope_threshold:
        signal = "BUY"
        status = "PRESSIONANDO_SUPORTE"

    return {
        "signal": signal,
        "status": status,
        "support": support,
        "resistance": resistance,
        "value": latest_close,
        "price_series": [float(item) for item in source_frame["close"].tail(24).tolist()],
    }
