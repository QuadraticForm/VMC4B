from typing import Union

from .config import Config
from .server import OscThreadServer
server = OscThreadServer()
config: Union[Config, None] = None
is_recording: bool = False
