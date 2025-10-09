from typing import get_type_hints


class AppConfigError(Exception):
    pass


TRUE_VALUES = {"true", "yes", "1"}


def _parse_bool(val: str | bool) -> bool:  # pylint: disable=E1136
    if isinstance(val, bool):
        return val
    return str(val).lower() in TRUE_VALUES


class AppConfig:
    """
    Map environment variables to class fields according to these rules:
      - Field won't be parsed unless it has a type annotation
      - Field will be skipped if not in all caps
      - Class field and environment variable name are the same
    """

    def __init__(self, env):
        for field in self.__annotations__:
            if not field.isupper():
                continue

            # Raise AppConfigError if required field not supplied
            default_value = getattr(self, field, None)
            if default_value is None and env.get(field) is None:
                raise AppConfigError(f"The {field} field is required")

            # Cast env var value to expected type and raise AppConfigError on failure
            try:
                var_type = get_type_hints(self.__class__)[field]
                if var_type is bool:
                    value = _parse_bool(env.get(field, default_value))
                else:
                    value = var_type(env.get(field, default_value))

                self.__setattr__(field, value)
            except ValueError:
                raise AppConfigError(
                    f'Unable to cast value of "{env[field]}"'
                    f'to type "{var_type}" for "{field}" field'
                ) from None

    def __repr__(self):
        return str(self.__dict__)
