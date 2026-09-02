import errors


def parse_phone_numbers_as_list(response_text: str, ignore_unknown: bool = True) -> list[str]:
    phone_numbers = []

    for raw_line in response_text.splitlines():
        line = raw_line.strip().strip("\u200e\u200f\ufeff")

        if not line or line.startswith("━") or line.startswith("🏢") or line.startswith("📊"):
            continue

        if "@" in line:
            _, _, content = line.partition("@")
            content = content.strip()

            if "unknown user" in content.lower():
                if not ignore_unknown:
                    raise errors.UnknownUserError("Unknown user found in response")
                continue

            digits_only = "".join(filter(str.isdigit, content))
            if 10 <= len(digits_only) <= 15:
                phone_numbers.append(digits_only)

    return phone_numbers