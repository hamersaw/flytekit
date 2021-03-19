import pytest
from mock import patch

from flytekit.common.exceptions.user import FlyteValueException
from flytekit.core import context_manager
from flytekit.core.context_manager import Image, ImageConfig
from flytekit.core.task import task
from flytekit.core.testing import patch as flyte_patch
from flytekit.core.workflow import ImperativeWorkflow

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = context_manager.SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)


@task
def t1(a: str) -> str:
    return a + " world"


wb = ImperativeWorkflow(name="my.workflow")
wb.add_workflow_input("in1", str)
node = wb.add_entity(t1, a=wb.inputs["in1"])
wb.add_workflow_output("from_n0t1", node.outputs["o0"])


def test_base_case():
    assert wb(in1="hello") == "hello world"


@patch("flytekit.core.workflow.ImperativeWorkflow.execute")
def test_error(mock_execute):
    mock_execute.return_value = None
    with pytest.raises(FlyteValueException):
        wb(in1="hello")


@flyte_patch(t1)
def test_none_conversion(mock_t1):
    mock_t1.return_value = None
    # This will try to convert None to a string
    with pytest.raises(AssertionError):
        wb(in1="hello")