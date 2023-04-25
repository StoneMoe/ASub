#!/usr/bin/env python3

from app import ui
from app.core import Core

if __name__ == '__main__':
    Core.init()
    # sentry_sdk.init(
    #     dsn="https://9e2193446dfc4c37a9ae78998ed0e140@o4504982470066176.ingest.sentry.io/4504982473867264",
    #     traces_sample_rate=1.0
    # )
    ui.launch()
