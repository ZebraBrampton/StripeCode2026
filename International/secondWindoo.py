import pygame
from os import environ

import matplotlib
matplotlib.use("Agg")                         # Use non-interactive Agg backend (no separate window)
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import io

from initialization import config

# ── Colours used by the graph renderer ───────────────────────────────────────
_TEMP_COL   = "#FF6B6B"   # Warm red for temperature
_RAIN_COL   = "#4FC3F7"   # Sky blue for rainfall
_WIND_COL   = "#81C784"   # Green for wind speed

_STOP_COL   = "#FF4444"
_SLOW_COL   = "#FFD700"
_FULL_COL   = "#44DD44"

_BG         = "#1A1A2E"   # Dark navy – matches the pygame overlay feel
_AXES_BG    = "#16213E"
_GRID       = "#2A2A4A"
_TEXT       = "#E0E0E0"


class RideWindow:
    def __init__(self, caption, size, pos, queue_in, queue_out, random_data, given_data):
        self.caption    = caption
        self.size       = size          # Original size kept for backward-compat; window is taller
        self.pos        = pos
        self.queue_in   = queue_in
        self.queue_out  = queue_out
        self.random_data = random_data
        self.given_data  = given_data

        self.main_log = None

        # Runtime flags
        self.running = True
        self.FPS     = 60

        # Position the OS window
        environ['SDL_VIDEO_WINDOW_POS'] = f"{pos[0]}, {pos[1]}"

        # ── Pygame init ───────────────────────────────────────────────────────
        pygame.init()

        # We need extra vertical space for the four graphs.
        # The stat section ends around y ≈ 510; each line graph ≈ 160 px tall,
        # bar graph ≈ 180 px tall, plus padding.
        self.GRAPH_AREA_TOP = 530        # y where graphs start (below stats list)
        self.LINE_H         = 155        # height of each individual line-graph panel
        self.BAR_H          = 185        # height of the bar-graph panel
        self.GRAPH_PAD      = 10         # vertical gap between panels

        # Total required height = graph area top + 3 line graphs + 1 bar graph + pads + margin
        total_height = (self.GRAPH_AREA_TOP
                        + 3 * (self.LINE_H + self.GRAPH_PAD)
                        + self.BAR_H
                        + 30)

        self.window_size = (self.size[0], total_height)   # width stays 400

        self.window = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption(self.caption)

        self.font       = pygame.font.SysFont("Arial", 18, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 14, bold=False)
        self.clock      = pygame.time.Clock()

        self.overlay = pygame.Surface(self.window_size, pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 100))

        # ── Simulation state ─────────────────────────────────────────────────
        self.curr_station     = "N/A"
        self.curr_hour        = config['simulation']['startHour']
        self.ride_statuses    = {}
        self.background_colour = (0, 0, 0)

        # ── History buffers (filled as hours tick by) ─────────────────────────
        # Each entry is added when weatherUpdate() is called
        self.history_hours  = []   # list of hour ints,  e.g. [10, 11, 12 …]
        self.history_temp   = []   # °C
        self.history_rain   = []   # raw intensity (0-10, labelled mm/hr on axis)
        self.history_wind   = []   # km/h from sim, displayed as m/s

        # Severe-impact counter  { ride_name : { "STOP": n, "SLOW": n } }
        self.severe_counts  = {}

        # Cache the last-rendered graph surface so we don't re-render every frame
        self._graph_surface  = None
        self._graph_dirty    = True    # set True whenever new data arrives

    # ─────────────────────────────────────────────────────────────────────────
    # Text helpers
    # ─────────────────────────────────────────────────────────────────────────
    def draw_text(self, text, colour, text_pos):
        surf = self.font.render(text, True, colour)
        rect = surf.get_rect(center=text_pos)
        self.window.blit(surf, rect)

    def draw_small_text(self, text, colour, text_pos):
        surf = self.small_font.render(text, True, colour)
        rect = surf.get_rect(center=text_pos)
        self.window.blit(surf, rect)

    # ─────────────────────────────────────────────────────────────────────────
    # Background
    # ─────────────────────────────────────────────────────────────────────────
    def draw_bg(self):
        self.window.fill(self.background_colour)
        self.window.blit(self.overlay, (0, 0))

    # ─────────────────────────────────────────────────────────────────────────
    # Weather / ride-status update  (called when a new hour message arrives)
    # ─────────────────────────────────────────────────────────────────────────
    def weatherUpdate(self):
        if self.main_log is None:
            return

        weather_values    = self.main_log[self.curr_hour]['weather_values']
        self.ride_statuses = self.main_log[self.curr_hour]['rides']

        # ── Append to history buffers ─────────────────────────────────────
        if self.curr_hour not in self.history_hours:
            self.history_hours.append(self.curr_hour)
            self.history_temp.append(weather_values['temp'])
            self.history_rain.append(weather_values['rain'])
            # Convert km/h → m/s  (1 km/h ≈ 0.2778 m/s)
            self.history_wind.append(round(weather_values['wind'] * 0.2778, 1))

        # ── Update severe-impact counters ─────────────────────────────────
        for ride, status in self.ride_statuses.items():
            if ride not in self.severe_counts:
                self.severe_counts[ride] = {"STOP": 0, "SLOW": 0}
            if status in ("STOP", "SLOW"):
                self.severe_counts[ride][status] += 1

        self._graph_dirty = True   # trigger a graph re-render

        # Forward combined packet to the park window
        self.queue_out.put({
            'weather': weather_values,
            'rides':   self.ride_statuses
        })

    # ─────────────────────────────────────────────────────────────────────────
    # Matplotlib → pygame surface conversion
    # ─────────────────────────────────────────────────────────────────────────
    def _fig_to_surface(self, fig):
        """Render a matplotlib figure to a pygame Surface via an in-memory PNG."""
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=96,
                    facecolor=_BG, edgecolor="none")
        buf.seek(0)
        surface = pygame.image.load(buf, "png")
        buf.close()
        plt.close(fig)
        return surface

    # ─────────────────────────────────────────────────────────────────────────
    # Build / cache the combined graph surface
    # ─────────────────────────────────────────────────────────────────────────
    def _render_graphs(self):
        """
        Draws four sub-figures onto one tall matplotlib figure and caches the
        result as a pygame Surface.  Only called when _graph_dirty is True.
        """
        W_IN  = self.size[0] / 96          # figure width  in inches (400 px @ 96 dpi)
        TOTAL_H_PX = (3 * (self.LINE_H + self.GRAPH_PAD)
                      + self.BAR_H + self.GRAPH_PAD)
        H_IN = TOTAL_H_PX / 96

        fig, axes = plt.subplots(
            4, 1,
            figsize=(W_IN, H_IN),
            gridspec_kw={"hspace": 0.6,
                         "height_ratios": [self.LINE_H, self.LINE_H,
                                           self.LINE_H, self.BAR_H]}
        )
        fig.patch.set_facecolor(_BG)

        hours = self.history_hours if self.history_hours else []

        # ── Helper: style a line-graph axis ──────────────────────────────
        def style_ax(ax, ylabel, title, colour, y_data):
            ax.set_facecolor(_AXES_BG)
            ax.set_title(title, color=_TEXT, fontsize=8, pad=3, fontweight="bold")
            ax.set_ylabel(ylabel, color=colour, fontsize=7, labelpad=3)
            ax.tick_params(colors=_TEXT, labelsize=6)
            ax.spines[:].set_color(_GRID)
            ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            ax.grid(color=_GRID, linestyle="--", linewidth=0.5, alpha=0.7)

            if hours and y_data:
                ax.plot(hours, y_data, color=colour, linewidth=1.8,
                        marker="o", markersize=3, zorder=3)
                # Shade under the curve
                ax.fill_between(hours, y_data, alpha=0.15, color=colour)
                # Annotate most recent value
                ax.annotate(f"{y_data[-1]}",
                            xy=(hours[-1], y_data[-1]),
                            xytext=(4, 4), textcoords="offset points",
                            color=colour, fontsize=6, fontweight="bold")
                ax.set_xlim(min(hours) - 0.3, max(hours) + 0.7)
            else:
                ax.text(0.5, 0.5, "Waiting for data…",
                        transform=ax.transAxes, ha="center", va="center",
                        color=_TEXT, fontsize=7)

            # X-axis labels as HH:00
            if hours:
                ax.set_xticks(hours)
                ax.set_xticklabels([f"{h}:00" for h in hours],
                                   rotation=30, ha="right", fontsize=5)

        # ── Panel 1: Temperature ──────────────────────────────────────────
        style_ax(axes[0], "°C", "Temperature Over Time",
                 _TEMP_COL, self.history_temp)

        # ── Panel 2: Rainfall intensity ───────────────────────────────────
        style_ax(axes[1], "mm/hr", "Rainfall Intensity Over Time",
                 _RAIN_COL, self.history_rain)

        # ── Panel 3: Wind speed ───────────────────────────────────────────
        style_ax(axes[2], "m/s", "Wind Speed Over Time",
                 _WIND_COL, self.history_wind)

        # ── Panel 4: Bar chart – most common severe impacts ───────────────
        ax4 = axes[3]
        ax4.set_facecolor(_AXES_BG)
        ax4.set_title("Most Common Severe Impacts per Ride",
                      color=_TEXT, fontsize=8, pad=3, fontweight="bold")
        ax4.tick_params(colors=_TEXT, labelsize=5.5)
        ax4.spines[:].set_color(_GRID)
        ax4.grid(axis="y", color=_GRID, linestyle="--",
                 linewidth=0.5, alpha=0.7)
        ax4.set_ylabel("Hours affected", color=_TEXT, fontsize=7, labelpad=3)

        if self.severe_counts:
            rides      = list(self.severe_counts.keys())
            stop_vals  = [self.severe_counts[r]["STOP"] for r in rides]
            slow_vals  = [self.severe_counts[r]["SLOW"] for r in rides]

            # Short ride labels (first word only) to save horizontal space
            short_labels = [r.split()[0] for r in rides]
            x = range(len(rides))
            bar_w = 0.35

            bars_stop = ax4.bar([i - bar_w/2 for i in x], stop_vals,
                                width=bar_w, color=_STOP_COL,
                                label="STOP", zorder=3)
            bars_slow = ax4.bar([i + bar_w/2 for i in x], slow_vals,
                                width=bar_w, color=_SLOW_COL,
                                label="SLOW", zorder=3)

            # Value labels on top of each bar
            for bar in list(bars_stop) + list(bars_slow):
                h = bar.get_height()
                if h > 0:
                    ax4.text(bar.get_x() + bar.get_width() / 2, h + 0.05,
                             str(int(h)), ha="center", va="bottom",
                             color=_TEXT, fontsize=5, fontweight="bold")

            ax4.set_xticks(list(x))
            ax4.set_xticklabels(short_labels, rotation=20,
                                ha="right", fontsize=5.5)
            ax4.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            ax4.legend(fontsize=6, framealpha=0.3,
                       labelcolor=_TEXT, facecolor=_AXES_BG,
                       edgecolor=_GRID)
        else:
            ax4.text(0.5, 0.5, "Waiting for data…",
                     transform=ax4.transAxes, ha="center", va="center",
                     color=_TEXT, fontsize=7)

        self._graph_surface = self._fig_to_surface(fig)
        self._graph_dirty   = False

    # ─────────────────────────────────────────────────────────────────────────
    # Main draw  (called every frame)
    # ─────────────────────────────────────────────────────────────────────────
    def draw(self):
        self.draw_bg()

        w = self.window_size[0]

        # ── Header info ───────────────────────────────────────────────────
        self.draw_text(f"Current Hour: {self.curr_hour}:00",
                       (255, 255, 255), (w // 2, 40))
        self.draw_text(f"Current Station: {self.curr_station}",
                       (255, 255, 255), (w // 2, 100))

        IMPACT_COLORS = {
            "FULL": (0, 255, 0),
            "SLOW": (255, 255, 0),
            "STOP": (255, 0, 0)
        }
        current_impact = self.ride_statuses.get(self.curr_station, "FULL")
        impact_color   = IMPACT_COLORS.get(current_impact, (255, 0, 0))
        self.draw_text(f"Current Impact: {current_impact}",
                       impact_color, (w // 2, 140))

        # ── Statistics list ───────────────────────────────────────────────
        self.draw_text("--- Current Statistics ---",
                       (200, 200, 200), (w // 2, 220))
        y_pos  = 260
        colors = {"FULL": (0, 255, 0), "SLOW": (255, 255, 0)}
        for ride, status in self.ride_statuses.items():
            color = colors.get(status, (255, 0, 0))
            self.draw_text(f"{ride}: {status}", color, (w // 2, y_pos))
            y_pos += 40

        # ── Divider label ─────────────────────────────────────────────────
        divider_y = self.GRAPH_AREA_TOP - 22
        pygame.draw.line(self.window, (80, 80, 120),
                         (10, divider_y), (w - 10, divider_y), 1)
        self.draw_small_text("── Weather & Impact Trends ──",
                             (160, 160, 220), (w // 2, divider_y - 8))

        # ── Graphs ────────────────────────────────────────────────────────
        if self._graph_dirty:
            self._render_graphs()

        if self._graph_surface is not None:
            # Scale the rendered surface to fit the available width exactly
            target_w = w - 4          # 2 px margin each side
            orig_w, orig_h = self._graph_surface.get_size()
            scale = target_w / orig_w
            target_h = int(orig_h * scale)
            scaled = pygame.transform.smoothscale(
                self._graph_surface, (target_w, target_h)
            )
            self.window.blit(scaled, (2, self.GRAPH_AREA_TOP))

    # ─────────────────────────────────────────────────────────────────────────
    # Events
    # ─────────────────────────────────────────────────────────────────────────
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.queue_out.put("QUIT")
                self.running = False

    # ─────────────────────────────────────────────────────────────────────────
    # Update  (message routing + display flip)
    # ─────────────────────────────────────────────────────────────────────────
    def update(self):
        try:
            msg = self.queue_in.get_nowait()

            if msg == "QUIT":
                self.running = False

            elif type(msg) == int:
                self.curr_hour = msg
                self.weatherUpdate()

            elif msg.startswith("run_"):
                if msg == "run_GIVEN":
                    self.main_log = self.given_data
                else:
                    self.main_log = self.random_data

            elif msg.startswith("S:"):
                self.curr_station = msg[2:].split("_")[0]
                raw_colour = msg[2:].split("_")[1].strip("()").split(",")
                self.background_colour = tuple(int(x.strip()) for x in raw_colour)

            elif msg == "RESTART":
                self.curr_station      = "N/A"
                self.curr_hour         = 10
                # Clear history so graphs reset cleanly
                self.history_hours     = []
                self.history_temp      = []
                self.history_rain      = []
                self.history_wind      = []
                self.severe_counts     = {}
                self._graph_surface    = None
                self._graph_dirty      = True

        except:
            pass

        pygame.display.flip()
        self.clock.tick(self.FPS)

    # ─────────────────────────────────────────────────────────────────────────
    # Main loop
    # ─────────────────────────────────────────────────────────────────────────
    def run(self):
        while self.running:
            self.draw()
            self.events()
            self.update()
        pygame.quit()