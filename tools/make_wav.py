"""Short bell tone for the HOME Menu banner."""
import math, struct, sys, wave

rate = 22050
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(rate)
    n = int(rate * 1.2)
    w.writeframes(b''.join(struct.pack('<h', int(9000 * math.exp(-3 * i / rate) * (math.sin(2 * math.pi * 523 * i / rate) + 0.4 * math.sin(2 * math.pi * 1310 * i / rate)))) for i in range(n)))
