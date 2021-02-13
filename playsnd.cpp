#include <SDL2/SDL.h>
#include <SDL2/SDL_mixer.h>
#include <iostream>
#include <string.h>

#define PLAYSND_VERSION "playsnd 1.0"


void usage() {
    std::cout << "usage: playsnd MUSIC_FILE_PATH\n";
}


void help() {
    usage();
    std::cout << "\nPlay a music file than quit application\n\n";
    std::cout << "Positional arguments:\n";
    std::cout << "  MUSIC_FILE_PATH       music file to play\n\n";
    std::cout << "Optional arguments:\n";
    std::cout << "  -h, -?, --help        show this help message and exit\n";
    std::cout << "  -v, --version         show program's version number and exit\n";
}



int main(int argc, char* argv[]){
        if(argc != 2) {
            usage();
            std::cerr << "Error: an audio output path mast be specified\n";
            std::cerr << "run \"playsnd -h\" for more details\n";
            return -1;
        }
        else if(strcmp(argv[1], "--help") == 0 ||
                strcmp(argv[1], "-?") == 0 ||
                strcmp(argv[1], "-h") == 0) {
            help(); return 0;
        }
        else if(strcmp(argv[1], "--version") == 0 ||
                strcmp(argv[1], "-v") == 0) {
            std::cout << PLAYSND_VERSION << "\n";
            return 0;
        }
        
        Mix_Music *music = NULL;

	// Initialize SDL.
	if (SDL_Init(SDL_INIT_AUDIO) < 0)
		return -1;
			
	//Initialize SDL_mixer 
	if( Mix_OpenAudio( 22050, MIX_DEFAULT_FORMAT, 2, 4096 ) == -1 ) 
		return -1; 
        
        // Load our music
	music = Mix_LoadMUS(argv[1]);
	if (music == NULL) {
                std::cerr << "Error: cannot read audio\n";
		return -1;
        }
        
        if ( Mix_PlayMusic( music, 1) == -1 )
		return -1;
		
	while ( Mix_PlayingMusic() ) ;
	
	Mix_FreeMusic(music);
	
	// quit SDL_mixer
	Mix_CloseAudio();
	
	return 0;
}

