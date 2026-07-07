from unittest.mock import MagicMock, patch

import backend.infrastructure.processing.quixstreams.consumer as consumer_module
from backend.infrastructure.processing.quixstreams.consumer import (
    QuixStreamsConsumerAdapter,
)


def test_adapter_builds_application_and_streams():
    app = MagicMock()
    with patch.object(consumer_module, "Application", return_value=app) as app_cls:
        adapter = QuixStreamsConsumerAdapter(consumer_group="grp")
        sdf = adapter.stream("some.topic")

    app_cls.assert_called_once()
    assert app_cls.call_args.kwargs["consumer_group"] == "grp"
    app.topic.assert_called_once_with("some.topic")
    app.dataframe.assert_called_once_with(app.topic.return_value)
    assert sdf is app.dataframe.return_value
