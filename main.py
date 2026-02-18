import pygame
import sys
from src.core.game_manager import GameManager
from src.core.game_state import GameStateType


def main():
    """游戏主入口"""
    game = GameManager()
    
    renderer = game.renderer
    renderer.init()
    
    ui_manager = game.ui_manager
    ui_manager.init_font()
    
    while game.running:
        dt = game.clock.tick(game.FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.quit()
            
            elif event.type == pygame.KEYDOWN:
                if game.game_state.is_menu():
                    if event.key == pygame.K_SPACE:
                        game.start_game(1)
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                        level = event.key - pygame.K_0
                        game.start_game(level)
                
                elif game.game_state.is_playing():
                    if event.key == pygame.K_ESCAPE:
                        game.game_state.change_state(GameStateType.PAUSED)
                
                elif game.game_state.is_paused():
                    if event.key == pygame.K_ESCAPE:
                        game.game_state.change_state(GameStateType.PLAYING)
                
                elif game.game_state.is_game_over():
                    if event.key == pygame.K_r:
                        game.reset()
                
                elif game.game_state.is_victory():
                    if event.key == pygame.K_SPACE:
                        next_level = min(game.current_level + 1, 5)
                        game.start_game(next_level)
                    elif event.key == pygame.K_r:
                        game.reset()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game.game_state.is_playing():
                    mouse_x, mouse_y = event.pos
                    
                    if event.button == 1:
                        if ui_manager.handle_click(mouse_x, mouse_y, game):
                            pass
                        elif ui_manager.selected_plant:
                            if game.grid:
                                row, col = game.grid.get_cell_from_position(mouse_x, mouse_y)
                                if game.grid.is_valid_cell(row, col) and not game.grid.is_cell_occupied(row, col):
                                    cost = ui_manager.get_selected_plant_cost()
                                    if game.spend_sun(cost):
                                        x, y = game.grid.get_cell_center(row, col)
                                        plant = ui_manager.create_plant(x, y)
                                        if plant:
                                            plant.row = row
                                            plant.col = col
                                            game.grid.place_plant(row, col, plant)
                                            game.add_plant(plant)
                    
                    elif event.button == 3:
                        ui_manager.selected_plant = None
                    
                    if game.sun_system:
                        game.sun_system.collect_sun(mouse_x, mouse_y, game)
        
        if game.game_state.is_playing():
            game.update(dt)
        
        game.screen.fill((34, 139, 34))
        
        if game.game_state.is_menu():
            renderer.render_menu(game.screen)
        
        elif game.game_state.is_playing():
            if game.grid:
                game.grid.render(game.screen)
            
            for plant in game.plants:
                plant.render(game.screen)
            
            for zombie in game.zombies:
                zombie.render(game.screen)
            
            for projectile in game.projectiles:
                projectile.render(game.screen)
            
            if game.sun_system:
                game.sun_system.render(game.screen)
            
            ui_manager.render(game.screen, game)
        
        elif game.game_state.is_paused():
            if game.grid:
                game.grid.render(game.screen)
            
            for plant in game.plants:
                plant.render(game.screen)
            
            for zombie in game.zombies:
                zombie.render(game.screen)
            
            renderer.render_paused(game.screen)
        
        elif game.game_state.is_game_over():
            if game.grid:
                game.grid.render(game.screen)
            
            for plant in game.plants:
                plant.render(game.screen)
            
            for zombie in game.zombies:
                zombie.render(game.screen)
            
            renderer.render_game_over(game.screen, game)
        
        elif game.game_state.is_victory():
            if game.grid:
                game.grid.render(game.screen)
            
            for plant in game.plants:
                plant.render(game.screen)
            
            renderer.render_victory(game.screen, game)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
