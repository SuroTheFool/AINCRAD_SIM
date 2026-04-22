# Project Description

## 1. Project Overview
Provide a high-level understanding of the project.

- **Project Name:**  Aincrad Simulator
- **Brief Description:**  My project is a casual game, The game is a rewarding character advancement-style system, challenging players to optimize their stats to overcome increasingly difficult monsters and reach the ultimate floor.
- **Problem Statement:**  The complexity and high barrier to entry of traditional RPG mechanics often discourage new players from engaging with the genre.   

- **Target Users:**  
    - Casual Players
  - Indie-game user
  - Infinite game user

- **Key Features:**  
    - click monster → earn gold → buy upgrades → challenge boss → unlock next floor → repeat.


---

## 2. Concept

### 2.1 Background
Explain the foundation of the project.

- Why this project exists  :

    The goal is to provide an accessible entry point to the RPG genre, delivering a fun, rewarding experience for both casual players and seasoned veterans.
- What inspired the project  :

    A streamlined "click-to-slay" economy inspired by Cookie Clicker, focusing on intuitive combat and rewarding character upgrades.

    Following the backstory of Sword Art Online, the game features a tower-climbing journey presented in a nostalgic, DS-era JRPG art style reminiscent of classic Pokémon titles.
- Importance of solving this problem  :

    Modern gamers often lack the time or mental energy for 100-hour, high-stress mechanics. This game easy to learn offer a deep satisfaction of progression and "improving" without the burnout of steep learning curves.

### 2.2 Objectives
Define the goals of the system.

- Clear objectives of the project  :

    Intuitive click-based mechanics, no learning curves of traditional RPGs, creating a low barrier for newcomers

    By eliminating "Game Over" states and health management, the game provides a purely satisfying experience where growth is continuous and never punitive.

    The "DS-era" visual style give a charming atmosphere that honors the legacy of classic RPG.




- What the system aims to achieve  :

    The "Flow State" Loop: Creating a seamless transition between active clicking (for speed) and passive damage (for progress) so players never feel "stuck."

    Infinite Scalability: Using mathematical growth formulas to ensure that as players reach higher floors, the numbers remain balanced yet huge

---

## 3. UML Class Diagram
Provide a UML class diagram that represents the system structure.

Your diagram must include:
- Classes  
- Attributes  
- Methods (optional but recommended)  
- Relationships (e.g., association, inheritance)

    [Click here to view my UML Class Diagram (PDF)](./UML_Diagram.pdf)

---

## 4. Object-Oriented Programming Implementation


- **Game** : The central controller that owns the main game loop and all subsystems.

- **Player** : Draw your character sprite sheet animation and handle all combat statistics (click damage, critical chance, critical multiplier, auto DPS, gold multiplier, strength, intelligence, endurance). 
    
-   **Monster** :  Represents a clickable enemy on the current floor. have HP, click detection via mask, sprite sheet animation, and HP bar rendering. Supports both static and animated sprites.

- **Menu** : Pause menu overlay used to save the current game state, load a previous save, or quit the game.

- **Shop** : Manages the upgrade overlay where the player spends Magic Stones. Upgrades, Skills, and Stats, applies purchased stat buffs directly to the Player instance.

- **BossRoom** : Manages boss raids that allow the player to progress to the next floor. Handles multiple enemy waves, a countdown timer, and victory/defeat state detection. Defeating the boss unlocks the next floor in the progression system.
- **QuestRoom** : Manages quest raid that allow the player to increase his stats and gain rewards. Handles multiple enemy waves, a countdown timer, and victory/defeat state detection. Defeating the last wave give a reward.
- **SkillBar** : In-game HUD displaying the five active skill slots and the endurance bar. Handles keyboard input for skill activation (keys 1–5, top row and numpad), renders skill icons, endurance cost labels, and duration drain bars for active effects.

---

## 5. Statistical Data

### 5.1 Data Recording Method

All statistical data will be stored in a CSV file (stats.csv).

Data will be analyzed using Python with pandas and matplotlib in a separate analysis.py file. statistical measures and visualizations are planned like this :


### 5.2 Data Features
Describe the characteristics of the data used in your system.

- Damage per click : Show damage evolution over time (time series)
- Monster defeated : Compare kills across floors (proportion)
- Gold spent : Compare kills across floors (proportion)

- Active-skill activation : Compare usage area across differents skills (proportion)



--- 

## 6. Changed Proposed Features (Optional)
If your final project differs from the original proposal, explain the changes here.

- What was changed  
- Why the change was made  

---

## 7. External Sources
Give credit for any external materials used in the project.

- Source code  
- Libraries or frameworks  
- Images, music, or artwork  

Include:
- Author/creator name  
- Source link (if available)  
- License information (if applicable)
