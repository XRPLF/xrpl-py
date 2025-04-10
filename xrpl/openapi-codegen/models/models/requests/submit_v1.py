from typing import Union
from xrpl.models.sign_and_submit_mode_v1 import SignAndSubmitModeV1
from xrpl.models.submit_only_mode import SubmitOnlyMode

SubmitRequestV1 = Union[SignAndSubmitModeV1, SubmitOnlyMode]
