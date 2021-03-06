#pragma once

#include "cinder/gl/Texture.h"
#include "bluegin/bluegin.h"
#include "bluegin/Graphic.h"
#include "bluegin/hgeFont.h"
#include "bluegin/Sound.h"

namespace bluegin {

struct ResourceConfig;

struct CachedTexture
{
    bool   active;
    string source;
    ci::gl::Texture texture;

    CachedTexture() : active(false) { }
};

class ResourceManager
{
public:
    ResourceManager();
    ~ResourceManager();

    void loadResourceConfig(const char* configPath);

    /**
     * Load a single named texture into GPU memory
     * @param texName texture name specified in resource config
     */
    bool acquireTexture(string texName);
    /**
     * Release GPU memory associated with named texture
     * @param texName texture name specified in resource config
     */
    void releaseTexture(string texName);
    /**
     * Load all textures from config file into GPU memory
     * @param updateGraphics call updateGraphics() after acquiring textures if true
     */
    void acquireAllTextures(bool updateGraphics=true);
    /**
     * Updates all graphic associations with active textures
     * Should be called after acquiring a new set of textures.
     */
    void updateGraphics();

    bool loadSound(SoundType type, ResourceConfig& rc);
    bool loadMusic(ResourceConfig& rc);

    ci::gl::Texture texture(string texName);
    Graphic         graphic(string graphicName);
    FontPtr         font(string fontName);
    AudioSourcePtr  sound(string soundName);

    //  Sound API designed for two scenarios:
    //  
    //  1.  One set of samples used throughout the app.  In this case call
    //      acquireAllSounds() once at the start of the App - all sounds are loaded
    //      and added to the SoundPool.
    //
    //  2.  Different sound sets used in different states (e.g. levels/worlds).
    //      Call releaseAllSounds() to clear the soundpool at the beginning of state
    //      create() and then call acquireSound to add each sound source for playback.
    //
    //  These calls have no effect on MUSIC_TYPE (streamed) sound sources

    //  Acquire a sound for playback
    void acquireSound(AudioSourcePtr sound);
    //  Acquire all the loaded sounds for playback
    void acquireAllSounds();
    //  Unprime all the sounds and initializes a new SoundPool
    void releaseAllSounds();

protected:
    ///  Save single texture configuration 
    bool loadTexture(ResourceConfig& rc);
    /**
     * Create a graphic with empty texture from configuration
     * Call updateGraphics() to associate active textures (for all entries)
     */
    bool loadGraphic(ResourceConfig& rc);

    /**
     * Loads a font and acquires associated texture
     */
    bool loadFont(ResourceConfig& rc);

    GLenum mMagFilter;
    GLenum mMinFilter;

    map<string, CachedTexture> mTextures;
    // map<string, ci::gl::Texture> mTextures;
    map<string, Graphic>         mGraphics;
    map<string, FontPtr>         mFonts;
    map<string, AudioSourcePtr>  mSounds;
};

typedef shared_ptr<ResourceManager> ResourceManagerPtr;

}
