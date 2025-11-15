import math

def estimate_bits(length, charset_size):
    if length <= 0 or charset_size <= 1:
        return 0.0
    return round(length * math.log2(charset_size), 1)

def classify(bits):
    if bits < 30:
        return "very weak"
    if bits < 45:
        return "weak"
    if bits < 60:
        return "okay for low risk accounts"
    if bits < 80:
        return "good for many accounts"
    return "strong"

def explain_pattern(pattern_type, length):
    if pattern_type == "only_digits":
        charset = 10
        note = "only digits, easy to guess by trial"
    elif pattern_type == "lowercase":
        charset = 26
        note = "only small letters, many common words"
    elif pattern_type == "lowercase_digits":
        charset = 36
        note = "letters and digits, better but still guessable if common pattern"
    elif pattern_type == "mixed_with_symbol":
        charset = 26 + 26 + 10 + 10
        note = "mix of letters, digits and a few symbols, stronger if not reused"
    else:
        charset = 20
        note = "rough guess, unknown pattern"
    bits = estimate_bits(length, charset)
    return bits, note

def main():
    print("Password pattern checker")
    print("Do not type real passwords.")
    print("Describe the pattern instead.")
    print("Examples: only_digits, lowercase, lowercase_digits, mixed_with_symbol\n")

    ptype = input("Pattern type: ").strip()
    try:
        length = int(input("Approximate length (number of characters): ").strip())
    except ValueError:
        print("Length must be a number.")
        return

    bits, note = explain_pattern(ptype, length)
    label = classify(bits)

    print("\nApproximate strength")
    print(f"- Estimated entropy: {bits} bits")
    print(f"- Category         : {label}")
    print(f"- Note             : {note}")
    print("Remember that reuse on many sites reduces real safety a lot.")

if __name__ == "__main__":
    main()
