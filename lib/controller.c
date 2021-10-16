// MSYS2 MinGW 64-bit
// pacman -S mingw-w64-x86_64-SDL2 mingw-w64-x86_64-gcc
// gcc -o controller.exe controller.c -lSDL2

#define SDL_MAIN_HANDLED
#include <SDL2/SDL.h>
#include <stdbool.h>
#include <stdio.h>

int main(int argc, char* args[]) {
    SDL_Init(SDL_INIT_JOYSTICK | SDL_INIT_VIDEO);
    SDL_GameController *ctrl = NULL;

    for (int i = 0; i < SDL_NumJoysticks(); ++i) {
        if (!SDL_IsGameController(i)) continue;
        ctrl = SDL_GameControllerOpen(i);
        //printf("Using game controller: %s", SDL_GameControllerName(ctrl));
        if (ctrl) break;
    }

    if (!ctrl) {
        SDL_GameControllerClose(ctrl);
        SDL_Quit();
        return 1;
    }

    while (1) {
        getchar();

        SDL_Event event;
        while (SDL_PollEvent(&event)) {}
        printf("%i %i %i %i %i\n", 
            SDL_GameControllerGetAxis(ctrl, SDL_CONTROLLER_AXIS_LEFTX),
            SDL_GameControllerGetAxis(ctrl, SDL_CONTROLLER_AXIS_LEFTY),
            SDL_GameControllerGetButton(ctrl, 0),
            SDL_GameControllerGetButton(ctrl, 2),
            SDL_GameControllerGetButton(ctrl, 9)
        );
        fflush(stdout);
    }
}
