from .prompt_level_1 import prompt_level_1
from .prompt_level_2 import prompt_level_2
from .prompt_level_3 import prompt_level_3

prompt_map = {
    "1단계": prompt_level_1,
    "2단계": prompt_level_2,
    "3단계": prompt_level_3,
}
