## A demo file for potentially how to allow a user to enter a prompt spanning multiple lines.

print("Enter/Paste your content. Press Enter on an empty line to finish.")
lines = []
while True:
    line = input()
    if line:  # Check if the line is not empty
        lines.append(line)
    else:
        break  # Exit the loop if an empty line is entered

multiline_text = '\n'.join(lines)
print("\nYour input:")
print(multiline_text)