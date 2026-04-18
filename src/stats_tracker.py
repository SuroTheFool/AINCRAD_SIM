
import csv
import os
import uuid
from datetime import datetime

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS_PATH = os.path.join(BASE_DIR, "saves", "stats.csv")

FIELDNAMES = ["timestamp", "event_type", "value", "metadata", "floor_id", "session_id"]


class StatsTracker:

    def __init__(self):
        self.session_id    = uuid.uuid4().hex[:8]   # ex: "a3f7c12b"
        self._playtime     = 0.0
        self._time_bucket  = 0.0
        self._ensure_file()

    # ------------------------------------------------------------------
    # SETUP
    # ------------------------------------------------------------------

    def _ensure_file(self):
        """Crée le CSV avec header si il n'existe pas encore."""
        os.makedirs(os.path.dirname(STATS_PATH), exist_ok=True)
        if not os.path.exists(STATS_PATH):
            with open(STATS_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()

    # ------------------------------------------------------------------
    # ENREGISTREMENT
    # ------------------------------------------------------------------

    def _write(self, event_type, value, metadata, floor_id):
        """Écrit une ligne dans le CSV."""
        row = {
            "timestamp"  : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event_type" : event_type,
            "value"      : value,
            "metadata"   : metadata,
            "floor_id"   : floor_id,
            "session_id" : self.session_id,
        }
        with open(STATS_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow(row)

    def record_damage(self, damage, is_crit, floor_id):
        """Appelé à chaque clic qui inflige des dégâts."""
        metadata = "crit" if is_crit else "normal"
        self._write("damage", int(damage), metadata, floor_id)

    def record_kill(self, monster_name, floor_id):
        """Called at the death of a monster."""
        self._write("kill", 1, monster_name, floor_id)

    def record_purchase(self, upgrade_id, cost, floor_id):
        """Called whenever a player buy an upgrade."""
        self._write("purchase", int(cost), upgrade_id, floor_id)

    def record_skill_use(self, skill_id, floor_id):
        """Appelé quand le joueur active un skill."""
        self._write("skill", 1, skill_id, floor_id)

    # ------------------------------------------------------------------
    # PLAYTIME — called in game every 10 seconds
    # ------------------------------------------------------------------

    def update(self, dt, floor_id):
        """Save 1 line every 10 seconds."""
        self._playtime    += dt
        self._time_bucket += dt
        if self._time_bucket >= 10.0:
            self._time_bucket -= 10.0
            self._write("playtime", 10, f"total_{int(self._playtime)}s", floor_id)