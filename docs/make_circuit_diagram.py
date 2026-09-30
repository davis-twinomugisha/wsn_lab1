import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D

fig, ax = plt.subplots(figsize=(9.5, 7.6), dpi=220)
ax.set_xlim(0, 13)
ax.set_ylim(-1.0, 8.6)
ax.axis("off")

navy = "#1f2d3d"
esp_fill = "#e8eef5"
sensor_fill = "#ffffff"
wire_red = "#c0392b"
wire_black = "#2b2b2b"
c_dht, c_ldr, c_pir = "#1a7f37", "#b8860b", "#d2691e"
c_led, c_buzz = "#6a0dad", "#0074b7"

ax.text(6.5, 8.3, "WSN Lab 1 — Multi-Sensor Edge Node Wiring",
        ha="center", va="top", fontsize=14, fontweight="bold", color=navy)

# ---------------- ESP32 board ----------------
esp_x, esp_y, esp_w, esp_h = 0.6, -1.0, 3.4, 8.0
ax.add_patch(FancyBboxPatch((esp_x, esp_y), esp_w, esp_h,
                             boxstyle="round,pad=0.02,rounding_size=0.12",
                             linewidth=1.8, edgecolor=navy, facecolor=esp_fill))
ax.text(esp_x + esp_w / 2, esp_y + esp_h - 0.35, "ESP32 DevKit V1",
        ha="center", va="center", fontsize=12.5, fontweight="bold", color=navy)
ax.text(esp_x + esp_w / 2, esp_y + esp_h - 0.68, "(USB to computer / Wokwi)",
        ha="center", va="center", fontsize=8.5, color=navy, style="italic")

pins = [("3V3", 5.65, wire_red), ("GND", 5.15, wire_black),
        ("D4", 4.35, c_dht), ("D34", 3.55, c_ldr), ("D27", 2.75, c_pir),
        ("D26", 1.35, c_led), ("D25", 0.55, c_buzz)]
pin_x = esp_x + esp_w
for label, y, color in pins:
    ax.plot([pin_x, pin_x + 0.22], [y, y], color=color, linewidth=2.4, zorder=3)
    ax.text(pin_x - 0.12, y, label, ha="right", va="center", fontsize=9.5, color=navy, fontweight="bold")
stub_x = pin_x + 0.22

# ---------------- Vertical bus rails for shared power/ground ----------------
rail_red_x = 5.55
rail_blk_x = 5.85

sensor_centers = {"dht": 6.9, "ldr": 4.55, "pir": 2.2}  # VCC pin y-height on each sensor box

ax.plot([rail_red_x, rail_red_x], [min(sensor_centers.values()), 5.65], color=wire_red, linewidth=2.0, zorder=1)
ax.plot([stub_x, rail_red_x], [5.65, 5.65], color=wire_red, linewidth=2.0, zorder=1)

ax.plot([rail_blk_x, rail_blk_x], [min(v - 0.3 for v in sensor_centers.values()), 5.15], color=wire_black, linewidth=2.0, zorder=1)
ax.plot([stub_x, rail_blk_x], [5.15, 5.15], color=wire_black, linewidth=2.0, zorder=1)

# ---------------- Sensor module boxes ----------------
def sensor_box(cx, top_y, w, h, title, subtitle, pin_defs):
    """pin_defs: list of (label, color, y_offset_from_top)"""
    x = cx - w / 2
    y = top_y - h
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                 boxstyle="round,pad=0.02,rounding_size=0.10",
                                 linewidth=1.6, edgecolor=navy, facecolor=sensor_fill))
    ax.text(cx, top_y - 0.30, title, ha="center", va="center", fontsize=11, fontweight="bold", color=navy)
    ax.text(cx, top_y - 0.58, subtitle, ha="center", va="center", fontsize=7.8, color=navy)
    pin_ys = {}
    for lbl, color, yoff in pin_defs:
        py = top_y - yoff
        ax.plot([x - 0.26, x], [py, py], color=color, linewidth=2.4, zorder=3)
        ax.text(x + 0.10, py, lbl, ha="left", va="center", fontsize=8.3, color=navy)
        pin_ys[lbl] = py
    return x, pin_ys

box_w, box_h = 3.0, 1.7
box_left_x = 8.6

_, dht_pins = sensor_box(box_left_x, 8.0, box_w, box_h, "DHT22", "Temperature + Humidity",
                          [("VCC", wire_red, 0.95), ("GND", wire_black, 1.25), ("SDA", c_dht, 1.55)])

_, ldr_pins = sensor_box(box_left_x, 5.65, box_w, box_h, "Photoresistor Module", "Light (analog AO)",
                          [("VCC", wire_red, 0.95), ("GND", wire_black, 1.25), ("AO", c_ldr, 1.55)])

_, pir_pins = sensor_box(box_left_x, 3.3, box_w, box_h, "PIR Motion Sensor", "Digital motion (OUT)",
                          [("VCC", wire_red, 0.95), ("GND", wire_black, 1.25), ("OUT", c_pir, 1.55)])

stub_left_x = box_left_x - box_w / 2 - 0.26

# ---------------- LED + buzzer (small, GPIO-driven, no shared VCC) ----------------
def small_box(cx, top_y, w, h, title, subtitle, pin_defs):
    x = cx - w / 2
    y = top_y - h
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                 boxstyle="round,pad=0.02,rounding_size=0.10",
                                 linewidth=1.4,
                                 edgecolor=navy, facecolor=sensor_fill))
    ax.text(cx, top_y - 0.28, title, ha="center", va="center", fontsize=9.5, fontweight="bold", color=navy)
    ax.text(cx, top_y - 0.52, subtitle, ha="center", va="center", fontsize=7.0, color=navy)
    pin_ys = {}
    for lbl, color, yoff in pin_defs:
        py = top_y - yoff
        ax.plot([x - 0.24, x], [py, py], color=color, linewidth=2.2, zorder=3)
        ax.text(x + 0.08, py, lbl, ha="left", va="center", fontsize=7.6, color=navy)
        pin_ys[lbl] = py
    return pin_ys

small_w, small_h = 1.55, 1.35
led_cx = box_left_x - 0.85
buzz_cx = box_left_x + 0.85
small_top_y = 1.35

led_pins = small_box(led_cx, small_top_y, small_w, small_h, "LED", "via 220Ω resistor",
                      [("GND", wire_black, 0.75), ("SIG", c_led, 1.0)])
buzz_pins = small_box(buzz_cx, small_top_y, small_w, small_h, "Buzzer", "event indicator",
                       [("GND", wire_black, 0.75), ("SIG", c_buzz, 1.0)])

stub_led_x = led_cx - small_w / 2 - 0.24
stub_buzz_x = buzz_cx - small_w / 2 - 0.24

# power rail -> each VCC
for pins_dict in (dht_pins, ldr_pins, pir_pins):
    ax.plot([rail_red_x, stub_left_x], [pins_dict["VCC"], pins_dict["VCC"]], color=wire_red, linewidth=1.8, zorder=1)
    ax.plot([rail_red_x, rail_red_x], [pins_dict["VCC"], 5.65], color=wire_red, linewidth=0.001)  # no-op keep

for pins_dict in (dht_pins, ldr_pins, pir_pins):
    ax.plot([rail_blk_x, stub_left_x], [pins_dict["GND"], pins_dict["GND"]], color=wire_black, linewidth=1.8, zorder=1)

# extend the vertical rails to actually reach each VCC/GND row (redraw full-span rails cleanly)
all_vcc_y = [dht_pins["VCC"], ldr_pins["VCC"], pir_pins["VCC"]]
all_gnd_y = [dht_pins["GND"], ldr_pins["GND"], pir_pins["GND"]]
ax.plot([rail_red_x, rail_red_x], [min(all_vcc_y), max(all_vcc_y + [5.65])], color=wire_red, linewidth=2.0, zorder=1)
ax.plot([rail_blk_x, rail_blk_x], [min(all_gnd_y), max(all_gnd_y + [5.15])], color=wire_black, linewidth=2.0, zorder=1)

# signal lines: direct diagonal from ESP32 D-pin stub to sensor signal pin
ax.plot([stub_x, stub_left_x], [4.35, dht_pins["SDA"]], color=c_dht, linewidth=1.8, zorder=2)
ax.plot([stub_x, stub_left_x], [3.55, ldr_pins["AO"]], color=c_ldr, linewidth=1.8, zorder=2)
ax.plot([stub_x, stub_left_x], [2.75, pir_pins["OUT"]], color=c_pir, linewidth=1.8, zorder=2)

# ---------------- LED / buzzer ground bus (routed low, clear of the boxes above) ----------------
gnd_bus_y = -0.35
ax.plot([rail_blk_x, rail_blk_x], [gnd_bus_y, max(all_gnd_y + [5.15])], color=wire_black, linewidth=2.0, zorder=1)
ax.plot([rail_blk_x, stub_buzz_x], [gnd_bus_y, gnd_bus_y], color=wire_black, linewidth=1.8, zorder=1)
ax.plot([stub_led_x, stub_led_x], [gnd_bus_y, led_pins["GND"]], color=wire_black, linewidth=1.8, zorder=1)
ax.plot([stub_buzz_x, stub_buzz_x], [gnd_bus_y, buzz_pins["GND"]], color=wire_black, linewidth=1.8, zorder=1)

# signal lines: ESP32 D26 -> LED, D25 -> Buzzer
ax.plot([stub_x, stub_led_x], [1.35, led_pins["SIG"]], color=c_led, linewidth=1.8, zorder=2)
ax.plot([stub_x, stub_buzz_x], [0.55, buzz_pins["SIG"]], color=c_buzz, linewidth=1.8, zorder=2)

# ---------------- Legend ----------------
legend_lines = [
    Line2D([0], [0], color=wire_red, lw=2.2, label="3V3 (power, shared)"),
    Line2D([0], [0], color=wire_black, lw=2.2, label="GND (shared)"),
    Line2D([0], [0], color=c_dht, lw=2.2, label="D4  -> DHT22 SDA"),
    Line2D([0], [0], color=c_ldr, lw=2.2, label="D34 -> Photoresistor AO"),
    Line2D([0], [0], color=c_pir, lw=2.2, label="D27 -> PIR OUT"),
    Line2D([0], [0], color=c_led, lw=2.2, label="D26 -> LED (via 220Ω)"),
    Line2D([0], [0], color=c_buzz, lw=2.2, label="D25 -> Buzzer"),
]
ax.legend(handles=legend_lines, loc="lower left", bbox_to_anchor=(0.005, 0.01),
          fontsize=8.3, frameon=True, framealpha=0.95, edgecolor=navy)

plt.tight_layout()
plt.savefig("circuit_diagram.png", dpi=220, bbox_inches="tight", facecolor="white")
print("saved")
