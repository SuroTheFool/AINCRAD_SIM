# Project Description

## 1. Project Overview
Provide a high-level understanding of the project.

- **Project Name:** Aincrad Simulator
- **Brief Description:** My project is a casual game featuring a rewarding character advancement-style system. It challenges players to optimize their stats to overcome increasingly difficult monsters and reach the ultimate floor.
- **Problem Statement:** The complexity and high barrier to entry of traditional RPG mechanics often discourage new players from engaging with the genre.
- **Target Users:**
    - Casual players
    - Indie game users
    - Infinite game users
- **Key Features:**
    - Click monster → earn gold → buy upgrades → challenge boss → unlock next floor → repeat.

---

## 2. Concept

### 2.1 Background
Explain the foundation of the project.

- **Why this project exists:**
    The goal is to provide an accessible entry point to the RPG genre, delivering a fun, rewarding experience for both casual players and seasoned veterans.
- **What inspired the project:**
    A streamlined "click-to-slay" economy inspired by Cookie Clicker, focusing on intuitive combat and rewarding character upgrades.
    Following the backstory of Sword Art Online, the game features a tower-climbing journey presented in a nostalgic, DS-era JRPG art style reminiscent of classic Pokémon titles.
- **Importance of solving this problem:**
    Modern gamers often lack the time or mental energy for 100-hour, high-stress mechanics. This game is easy to learn and offers a deep satisfaction of progression and improvement without the burnout of steep learning curves.

### 2.2 Objectives
Define the goals of the system.

- **Clear objectives of the project:**
    - **Accessibility:** Intuitive click-based mechanics with none of the learning curves of traditional RPGs, creating a low barrier for newcomers.
    - **Stress-Free Progression:** By eliminating "Game Over" states and health management, the game provides a purely satisfying experience where growth is continuous and never punitive.
    - **Atmospheric Nostalgia:** The "DS-era" visual style gives a charming atmosphere that honors the legacy of classic RPGs.
- **What the system aims to achieve:**
    - **The "Flow State" Loop:** Creating a seamless transition between active clicking (for speed) and passive damage (for progress) so players never feel "stuck."
    - **Infinite Scalability:** Using mathematical growth formulas to ensure that as players reach higher floors, the numbers remain balanced yet substantial.

---

## 3. UML Class Diagram

[Click here to view my UML Class Diagram (PDF)](./uml_diagram.pdf)

---

## 4. Object-Oriented Programming Implementation

- **Game:** The central controller that owns the main game loop and all subsystems.
- **Floor** Manages the visual layout of the current floor the player is on, including layered backgrounds and decorations. Handles monster spawning with a weighted probability system
- **Player:** Manages character sprite sheet animations and handles all combat statistics including click damage, critical chance, critical multiplier, auto DPS, gold multiplier, strength, intelligence, and endurance.
- **Monster:** Represents a clickable enemy on the current floor. Features include HP, click detection via mask, sprite sheet animation, and HP bar rendering. Supports both static and animated sprites.
- **Mob (extends Monster)** Monster with dialog bubble support. Triggers speech bubbles at specific HP thresholds during combat.
- **Ally (extends Monster)**  Friendly entity that appears during quests. Deals automatic DPS to living targets, displays wave-specific dialog bubbles, and disappears between waves based on quest configuration.
- **Menu:** Pause menu overlay used to save the current game state, load a previous save, or quit the game.
- **Handles** serialization and deserialization of the full game state to a JSON file. Rebuilds player stats on load by replaying all purchased upgrades
- **Shop:** Manages the upgrade overlay where the player spends Magic Stones on upgrades, skills, and stats. It applies purchased stat buffs directly to the Player instance.
- **BossRoom:** Manages boss raids that allow the player to progress to the next floor. Handles multiple enemy waves, a countdown timer, and victory/defeat state detection. Defeating the boss unlocks the next floor in the progression system.
- **QuestRoom:** Manages quest raids that allow the player to increase stats and gain rewards. Handles multiple enemy waves, a countdown timer, and victory/defeat state detection. Defeating the last wave grants a reward.
- **SkillBar:** In-game HUD displaying the five active skill slots and the endurance bar. Handles keyboard input for skill activation (keys 1–5, top row and numpad), and renders skill icons, endurance cost labels, and duration drain bars for active effects.
- **StatsTracker** Records gameplay events (damage dealt, monsters killed, purchases, skill activations, playtime) into a CSV file. Each session is identified by a unique session ID
- **SaveManager** Handles serialization and deserialization of the full game state to a JSON file. Rebuilds player stats on load by replaying all purchased upgrades

---

## 5. Statistical Data

### 5.1 Data Recording Method

All statistical data will be stored in a CSV file (`stats.csv`). Data will be analyzed using Python with pandas and matplotlib in a separate `analysis.py` file. Statistical measures and visualizations are planned as follows:

### 5.2 Data Features
Describe the characteristics of the data used in your system.

- **Damage per click:** Shows damage evolution over time (time series).
- **Monster defeated:** Compares kills across floors (proportion).
- **Gold spent:** Compares spending across floors (proportion).
- **Active-skill activation:** Compares usage frequency across different skills (proportion).

---

## 6. Changed Proposed Features

- A quest system was added beyond the requirements. This quest system helps the game reduce the weakness of repetitive features while adding Lore to the experience.

---

## 7. External Sources

### Credits for the assets used in my game:

For sound effects and music, if no specific website is credited, it indicates the asset was sourced from YouTube.

- **Icons:** Flaticon free right pictures (Smashicons) / Generative AI
- **SFX:**
    - **Main Menu:** YouTube • Channel: Orwa Farran, Game MainMenu Music (4th Album) / Copyright free music
    - **Game Started:** Freesound.org • EilasSFX
    - **BossRaid:** 'Endless Storm' by Makai-symphony | War Music (No Copyright) - Author: BreakingCopyright & Creative Commons
    - **First Town:** Happy Village Town Royalty Free Music - YouTube Motion Array & Creative Commons
    - **Hit Sounds:** SWORD SLASH SOUND EFFECT | NO COPYRIGHT - BAROGS GAMING & Creative Commons
    - **Death Sound:** Big explosion sound effect - Lightning editor & Creative Commons
    - **Buy SFX:** Pop Sound Effect - universalsoundeffects & Creative Commons
