# Rendering Directly to HDMI on a Raspberry Pi via the Linux Framebuffer

This tutorial shows how to render graphics directly to an HDMI display on a Raspberry Pi by writing to the Linux framebuffer at `/dev/fb0`.

The approach comes from Dr. Frankintosh’s Raspberry Pi framebuffer demonstration. The core idea is to:

1. Create graphics in Python using Pillow.
2. Keep those graphics in an in-memory RGBA bitmap.
3. Convert the bitmap from 32-bit RGBA into the 16-bit RGB565 format expected by the framebuffer.
4. Write the resulting bytes directly to `/dev/fb0`.
5. Move the expensive RGBA → RGB565 conversion into C so Python can render at a usable speed.

This avoids running a full graphical desktop and is particularly useful on resource-constrained Raspberry Pis such as the Pi Zero 2 W.

---

## 1. Understanding the Framebuffer

On Linux, the framebuffer exposes display memory as a device file.

In the video, the framebuffer is:

```text
/dev/fb0
```

Writing bytes to that device changes what appears on the HDMI display.

For the setup demonstrated in the video, the HDMI display is:

```text
1920 × 1080
```

and each framebuffer pixel occupies:

```text
16 bits
2 bytes
```

The pixel format is **RGB565**:

```text
RRRRRGGGGGGBBBBB
```

That means:

* Red: 5 bits
* Green: 6 bits
* Blue: 5 bits

Red and blue can therefore represent values from 0–31, while green can represent values from 0–63.

At 1920×1080, that is more than two million pixels and roughly four million framebuffer bytes per complete screen update.

---

## 2. Why Pillow Cannot Be Written Directly to the Framebuffer

Pillow makes drawing convenient, but its bitmap representation does not match the framebuffer format.

The video creates a Pillow image using:

```text
RGBA
```

That means each pixel contains:

```text
8 bits red
8 bits green
8 bits blue
8 bits alpha
```

The framebuffer instead wants a packed 16-bit RGB565 pixel.

So this:

```text
R R R R R R R R
G G G G G G G G
B B B B B B B B
```

has to become:

```text
RRRRRGGGGGGBBBBB
```

before the image can be displayed. The alpha channel is not needed.

This conversion step is the main performance problem.

---

# Part 1 — Prove That `/dev/fb0` Works

Before building a graphics system, verify that you can actually write to the framebuffer.

## 3. Hard-Clearing the Screen

Dr. Frankintosh begins with a simple `hard_clear` operation.

Conceptually, it looks like this:

```python
FRAMEBUFFER = "/dev/fb0"

def hard_clear(pixel_bytes):
    with open(FRAMEBUFFER, "wb") as fb:
        fb.write(
            pixel_bytes *
            SCREEN_WIDTH *
            SCREEN_HEIGHT
        )
```

The important operation is:

```python
open("/dev/fb0", "wb")
```

followed by writing the framebuffer data directly to the device.

A black screen can be produced by filling the framebuffer with zeros.

The video then demonstrates other RGB565 values, including white, red, green, and blue, to prove that framebuffer writes are reaching the HDMI output.

At this point the pipeline is simply:

```text
Python
   │
   ▼
RGB565 bytes
   │
   ▼
/dev/fb0
   │
   ▼
HDMI display
```

---

# Part 2 — Use Pillow as a Back Buffer

Writing repeated colors is useful for testing, but real applications need individual pixels, shapes, text, and images.

That is where Pillow comes in.

## 4. Create an RGBA Bitmap

Create an in-memory Pillow image matching the display dimensions.

Conceptually:

```python
from PIL import Image, ImageDraw

self.bitmap = Image.new(
    "RGBA",
    (self.width, self.height)
)

self.draw = ImageDraw.Draw(self.bitmap)
```

This bitmap becomes your **back buffer**.

Instead of drawing directly to HDMI, your application draws into this Pillow image.

The rendering architecture becomes:

```text
Application
     │
     ▼
Pillow ImageDraw
     │
     ▼
RGBA bitmap in RAM
     │
     ▼
RGBA → RGB565 conversion
     │
     ▼
/dev/fb0
     │
     ▼
HDMI
```

---

## 5. Add Drawing Operations

Because Pillow supplies an `ImageDraw` object, the screen abstraction can expose convenient methods such as:

```python
screen.line(...)
screen.rectangle(...)
```

These methods simply forward operations to Pillow.

For example:

```python
def line(self, coords, fill):
    self.draw.line(coords, fill=fill)

def rectangle(self, coords, fill):
    self.draw.rectangle(coords, fill=fill)
```

The video demonstrates this by drawing:

* a red rectangle
* a green line
* a blue line

and then flushing the completed bitmap to the framebuffer.

The useful design principle here is:

```text
DRAW MANY THINGS
       │
       ▼
Pillow back buffer
       │
       ▼
flush()
       │
       ▼
HDMI
```

You do not need to touch the framebuffer every time a line or rectangle is drawn.

---

# Part 3 — Convert RGBA into RGB565

## 6. RGB888 to RGB565 Conversion

For each Pillow pixel, you obtain:

```text
R = 0–255
G = 0–255
B = 0–255
```

You need to reduce these to:

```text
R = 5 bits
G = 6 bits
B = 5 bits
```

Conceptually:

```python
r5 = r >> 3
g6 = g >> 2
b5 = b >> 3
```

Then pack them into one 16-bit value:

```python
rgb565 = (r5 << 11) | (g6 << 5) | b5
```

The resulting bit layout is:

```text
15                         0
│                          │
RRRRR GGGGGG BBBBB
```

This is the bit manipulation Dr. Frankintosh describes when converting every Pillow pixel into the framebuffer representation.

---

## 7. The Slow Python Implementation

The straightforward implementation is to walk through the bitmap one pixel at a time:

```text
for every row:
    for every pixel:
        get red
        get green
        get blue

        convert RGB888 → RGB565

        append two output bytes
```

Once the complete framebuffer byte array has been generated:

```python
with open("/dev/fb0", "wb") as fb:
    fb.write(framebuffer_data)
```

The problem is performance.

For a 1920×1080 screen, Python has to perform the conversion more than two million times for every complete frame.

In the video, even performing what is effectively a screen clear this way takes visibly long enough that row numbers are printed while the conversion runs.

This establishes an important result:

```text
Pillow drawing:
FAST ENOUGH

Python per-pixel RGB conversion:
TOO SLOW
```

---

# Part 4 — Move the Conversion into C

The solution demonstrated in the video is not to abandon Python.

Instead, Python continues doing the high-level rendering while C performs the expensive pixel conversion.

The final architecture is:

```text
┌──────────────────────────────┐
│            Python            │
│                              │
│ Application logic            │
│ Pillow drawing               │
│ Text                         │
│ Lines                        │
│ Rectangles                   │
└──────────────┬───────────────┘
               │
               │ RGBA bytes
               ▼
┌──────────────────────────────┐
│        C Extension           │
│                              │
│ RGBA → RGB565                │
│ conversion                   │
└──────────────┬───────────────┘
               │
               │ RGB565 bytes
               ▼
┌──────────────────────────────┐
│          /dev/fb0            │
└──────────────┬───────────────┘
               │
               ▼
             HDMI
```

This preserves Python's convenience while moving the expensive byte manipulation into compiled code.

---

## 8. The C Conversion Function

The C extension receives several things from Python:

```text
RGBA pixel data
data length
width
height
```

It then:

1. Calculates the framebuffer size.
2. Allocates enough output memory.
3. Walks through the RGBA image.
4. Reads red, green, and blue.
5. Shifts the bits into RGB565 positions.
6. Writes the packed pixels into the output buffer.
7. Converts the result back into a Python bytes object.
8. Frees the temporary C memory.
9. Returns the bytes to Python.

That process is described directly in the video.

A simplified representation of the conversion itself would look something like:

```c
uint16_t pixel =
    ((red   >> 3) << 11) |
    ((green >> 2) << 5)  |
    ((blue  >> 3));
```

The precise extension source code is **not included verbatim in the supplied transcript**, so treat this as an illustration of the bit-packing operation rather than a transcription of Dr. Frankintosh's source.

---

# Part 5 — Expose the C Code to Python

## 9. Build a CPython Extension

The video wraps the conversion routine as a Python-callable C extension.

A Python setup file defines:

* the extension/module name
* the C source file
* version information
* description
* module configuration

The build script then invokes Python's setup process to compile the C source into a shared object on the Raspberry Pi.

The resulting file is an ARM CPython shared object that Python can import like a normal module.

Conceptually:

```python
from framebuffer_c import rgba_to_rgb565
```

Again, the transcript describes this build process but does not provide the complete `setup.py` listing.

---

## 10. Obtain Raw Pillow Bytes

Once the extension exists, Python needs to send it the raw bitmap.

Conceptually:

```python
rgba = self.bitmap.tobytes()
```

Then:

```python
rgb565 = rgba_to_rgb565(
    rgba,
    self.width,
    self.height
)
```

The C extension returns framebuffer-ready bytes.

The video describes exactly this flow: obtain the raw image bytes, call the C conversion function, open the framebuffer, and write the result.

---

# Part 6 — Implement `flush()`

The screen abstraction can now expose a single operation:

```python
screen.flush()
```

A conceptual implementation is:

```python
def flush(self):
    rgba = self.bitmap.tobytes()

    rgb565 = rgba_to_rgb565(
        rgba,
        self.width,
        self.height
    )

    with open("/dev/fb0", "wb") as fb:
        fb.write(rgb565)
```

Now your main application can remain clean:

```python
screen.rectangle(...)
screen.line(...)
screen.line(...)
screen.flush()
```

The expensive transformation happens only during `flush()`.

---

## 11. Keep Slow and Fast Renderers During Development

Dr. Frankintosh keeps both implementations available.

The screen object can select between:

```text
slow flush
```

and:

```text
fast flush
```

Conceptually:

```python
def flush(self):
    if self.fast_flush:
        self._fast_write_framebuffer()
    else:
        self._slow_write_framebuffer()
```

The slow renderer is useful because it provides a straightforward reference implementation.

The fast renderer uses the compiled C converter.

With the fast implementation enabled, the video shows the display flashing white and then almost immediately displaying the Pillow-rendered rectangle and lines.

---

# Part 7 — Suggested Project Structure

Based on the structure described in the video, a project could be organized approximately like this:

```text
framebuffer-demo/
│
├── main.py
├── screen.py
│
├── cabb.c
├── setup.py
│
├── build.sh
├── run.sh
│
└── requirements.txt
```

The transcript specifically describes:

```text
main.py
```

as the application framework,

a screen object responsible for framebuffer rendering,

a C source file used to build the Python extension,

a setup script for compiling it,

and shell scripts for building the virtual environment and running the program.

The exact filenames and complete contents of every file are not fully reproduced in the transcript, so this structure should be treated as a reconstruction of the demonstrated architecture rather than an exact repository listing.

---

# Part 8 — Application Loop

Once everything is working, application code no longer needs to care about RGB565.

It operates entirely in normal Pillow coordinates and colors.

For example:

```python
screen.rectangle(
    (10, 10, 1910, 1070),
    fill=(255, 0, 0, 255)
)

screen.line(
    (10, 540, 1910, 540),
    fill=(0, 255, 0, 255)
)

screen.line(
    (960, 10, 960, 1070),
    fill=(0, 0, 255, 255)
)

screen.flush()
```

Pillow sees:

```text
RGBA
```

Your application sees:

```text
normal Python graphics
```

The C extension sees:

```text
millions of pixels to convert
```

and `/dev/fb0` receives:

```text
packed RGB565
```

That separation is what makes the design useful.

---

# The Complete Rendering Pipeline

The entire system can be summarized as:

```text
                 PYTHON
                   │
                   │
            Application logic
                   │
                   ▼
             Pillow Image
             1920 × 1080
                 RGBA
                   │
                   │ .tobytes()
                   ▼
              C EXTENSION
                   │
                   │
            RGBA → RGB565
                   │
                   ▼
          framebuffer bytes
                   │
                   ▼
              /dev/fb0
                   │
                   ▼
                  HDMI
```

---

# Why This Approach Works

The design divides the workload according to what each language does well.

### Python handles

```text
Application logic
Drawing commands
Text
Geometry
UI/dashboard logic
Pillow
```

### C handles

```text
Millions of repeated bit operations
RGBA → RGB565 packing
High-speed pixel conversion
```

### Linux handles

```text
/dev/fb0
        ↓
display hardware
        ↓
HDMI
```

The important insight from the demonstration is that direct framebuffer rendering itself is straightforward. The expensive part is converting a large Pillow image into the pixel format expected by the framebuffer.

Doing that conversion one pixel at a time in Python is too slow for this use case; moving only that conversion routine into C makes the overall Python-based graphics system practical.

---

# Minimal Mental Model

If you remember only five things, remember these:

```text
1. Draw into a Pillow RGBA image.

2. Get the raw RGBA bytes.

3. Convert every pixel:
      RGB888 → RGB565

4. Perform that conversion in C rather than
   a Python per-pixel loop.

5. Write the resulting byte buffer to:
      /dev/fb0
```

That gives you a lightweight rendering path:

```text
Python + Pillow
      ↓
tiny C accelerator
      ↓
Linux framebuffer
      ↓
HDMI
```

without requiring your application to render through the Raspberry Pi desktop environment.
