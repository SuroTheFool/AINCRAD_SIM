import sys
import os
import traceback
import pygame

# ── Error log path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "venv_export/error.log")


def _log_error(exc: Exception):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write("\n[FATAL ERROR]\n")
            traceback.print_exc(file=f)
    except Exception:
        pass


def _show_loading_screen(screen, font, message="Loading..."):
    screen.fill((10, 0, 20))
    surf = font.render(message, True, (200, 180, 180))
    screen.blit(surf, surf.get_rect(center=(screen.get_width() // 2,
                                            screen.get_height() // 2)))
    pygame.display.flip()
    pygame.event.pump()


def main():
    try:
        pygame.init()

        # Mixer init is optional — no audio device = silent mode, no crash
        try:
            pygame.mixer.init()
        except pygame.error as e:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"\n[Audio] Mixer init failed : {e}\n")

        from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)

        loading_font = pygame.font.SysFont("Verdana", 22)

        while True:
            _show_loading_screen(screen, loading_font, "Loading...")

            from src.main_menu import MainMenu
            menu   = MainMenu(screen)
            result = menu.run()

            if result == "quit":
                break

            _show_loading_screen(screen, loading_font, "Loading world...")

            from src.game import Game
            game = Game(screen)
            game.run()

    except Exception as e:
        _log_error(e)
        try:
            screen.fill((20, 0, 0))
            font = pygame.font.SysFont("Verdana", 16)
            lines = [
                "A fatal error occurred.",
                "See error.log for details.",
                "",
                str(e)[:80],
            ]
            for i, line in enumerate(lines):
                surf = font.render(line, True, (255, 100, 100))
                screen.blit(surf, (40, 40 + i * 28))
            pygame.display.flip()
            pygame.time.wait(4000)
        except Exception:
            pass
        sys.exit(1)

    finally:
        pygame.quit()


if __name__ == "__main__":
    main()