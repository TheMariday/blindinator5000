import sdl2.ext
import time

if __name__ == "__main__":

    sdl2.ext.init()

    # window = sdl2.ext.Window("Hello World!", size=(3840, 2160), flags=sdl2.SDL_WINDOW_BORDERLESS | sdl2.SDL_WINDOW_FULLSCREEN)
    window = sdl2.ext.Window("Hello World!", size=(1280, 720))

    window.show()

    renderer = sdl2.ext.Renderer(
        window, flags=sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC
    )

    tst_img = sdl2.ext.load_bmp("resources/hello.bmp")
    tx = sdl2.ext.Texture(renderer, tst_img)

    c = 0
    start = time.time()
    while True:
        renderer.clear()
        renderer.copy(tx, dstrect=(c, 0, 100, 100), angle=20)
        renderer.present()
        c += 1

        print(f"fps: {int(c / (time.time() - start))}")

    sdl2.ext.quit()
