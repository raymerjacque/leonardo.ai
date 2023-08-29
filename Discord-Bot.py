import discord
from discord.ext import commands
import requests
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
import urllib3
import argparse
import io
import random
import json
import asyncio
import httpx
from httpx import AsyncClient
from httpx import TimeoutException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Argument parsing
parser = argparse.ArgumentParser(description="Run the Discord bot with optional SSL for an embedded server.")
parser.add_argument('--ssl-keyfile', type=str, help='Path to the SSL key file.', default=None)
parser.add_argument('--ssl-certfile', type=str, help='Path to the SSL certificate file.', default=None)
args = parser.parse_args()

print("Starting bot...")

TOKEN = 'PUT YOUR DISCORD BOT TOKEN HERE'
CHANNEL_ID = 123456789  # Replace with your Discord channel ID, This is where the images will be sent
channel_input_id = 123456789  # Replace with your Discord channel ID, This is where the user will issue the !generate command.

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

style_descriptions = {
    "ABSTRACT_CITYSCAPE": "abstract cityscape, Ultra Realistic Cinematic Light abstract, futuristic, cityscape, out of focus background and incredible 16k resolution produced in Unreal Engine 5 and Octane Render",
    "ABSTRACT EXPRESSIONISM": "abstract expressionist style, gestural brushstrokes, bold and expressive, emotional and spontaneous, Jackson Pollock-inspired, non-representational",
    "ABSTRACT_VIBRANT": "vibrant, editorial, abstract elements, colorful, color splatter, realism, inspired by the style of Ryan Hewett, dynamic realism, soft lighting and intricate details",
    "AQUASTIC": "graceful movement with intricate details, inspired by artists like Lotte Reiniger, Carne Griffiths and Alphonse Mucha. Dreamy and surreal atmosphere, twirling in an aquatic landscape with water surface",
    "AQUATIC": "vast and diverse underwater ecosystems, vivid blues and greens, ethereal lighting, sea creatures, coral reefs, undulating oceanic forms. The atmosphere is tranquil, inviting exploration and discovery. Techniques include gradient shading, texturing to mimic water surfaces, and a blend of realism and fantasy. Key influences might include traditional marine art, scientific illustrations, and the fantastical representations of the sea in animated films.",
    "AMAZONIAN": "Amazonian cave, landscape, jungle, waterfall, moss-covered ancient ruins, dramatic lighting and intense colors, mesmerizing details of the environment and breathtaking atmosphere",
    "ANIME": "anime atmospheric, atmospheric anime, anime character; full body art, digital anime art, beautiful anime art style, anime picture, anime arts, beautiful anime style, digital advanced anime art, anime painting, anime artwork, beautiful anime art, detailed digital anime art, anime epic artwork",
    "ARCHITECTURE": "modern architecture design, luxury architecture, bright, very beautiful, trending on Unsplash, breathtaking, special lighting effects, extreme lighting",
    "ART": "Painting, by Salvador Dali, allegory, surrealism, religious art, genre painting, portrait, painter, still life",
    "ASSET_RENDER": "isometric, polaroid Octane Render, 3D render 1.5 0 mm lens, KeyShot product render, rendered, KeyShot product render Pinterest, 3D product render, 3D CGI render, 3D CGI render, ultra wide-angle isometric view",
    "AVATAR": "avatar movie, avatar with blue skin, vfx movie, cinematic lighting, utopian jungle, pandora jungle, sci-fi nether world, lost world, pandora fantasy landscape, lush green landscape, high quality render",
    "BAUHAUS": "Bauhaus art movement, by Wassily Kandinsky, Bauhaus style painting, geometric abstraction, vibrant colors, painting",
    "CANDYLAND": "candy land style, whimsical fantasy landscape art, japanese pop surrealism, colorful digital fantasy art, made of candy and lollipops, whimsical and dreamy",
    "CARTOON": "modern day cartoon style, children’s cartoons shown on TV networks, playful and entertaining cartoons, bold outlines, bright colors, and exaggerated features, oversized eyes, face and feature,  playful energy to a colorful world, cinematic lighting, detailed characters, Beautiful lively background, sunshafts, cinematic lighting, spectacular lighting, very detailed, beautiful",
    "CLAYMATION": "clay animation, as a claymation character, claymation style, animation key shot, plasticine, clay animation, stopmotion animation, aardman character design, plasticine models",
    "COLORING_BOOK": "line art illustration, lineart Behance HD, illustration line art style, line art coloring page, decora inspired illustrations, coloring pages, digital line-art, line art!!, thick line art, coloring book page, clean coloring book page, black ink line art, coloring page, detailed line art",
    "COMIC_BOOK": "Comic cover, 1960s Marvel comic, comic book illustrations",
    "COSMIC": "in cosmic atmosphere, humanitys cosmic future, space art concept, space landscape, scene in space, cosmic space, beautiful space star planet, background in space, realistic, cinematic, breathtaking view",
    "CUBISM": "cubist Picasso, cubism, a cubist painting, heavy cubism, cubist painting, by Carlo Carrà, style of Picasso, modern cubism, futuristic cubism",
    "CYBERPUNK": "synthwave image, (neotokyo), dreamy colorful cyberpunk colors, cyberpunk Blade Runner art, retrofuturism, cyberpunk, beautiful cyberpunk style, CGSociety 9",
    "DIGITAL GLITCH ART": "Highly saturated and contrasting colors, heavy use of black and bright neons, Texture Pixelated, distorted, or 'glitchy', this style intentionally harnesses digital errors for aesthetic effect, Abstract form, irregular, and chaotic, often featuring repeated motifs or patterns, Can evoke feelings of confusion, excitement, and a sense of being 'plugged in' to the digital age",
    "DISNEY": "styled in a mix of modern disney cartoon and anime, cinematic lighting, detailed characters, Beautiful lively background, sunshafts, cinematic lighting, spectacular lighting, very detailed, beautiful",
    "DYSTOPIAN": "cifi world, cybernetic civilizations, peter gric and dan mumford, brutalist dark futuristic, dystopian brutalist atmosphere, dark dystopian world, cinematic 8k, end of the world, doomsday",
    "ELVEN": "elven lifestyle, photoreal, realistic, 32k quality, crafted by Elves and engraved in copper, elven fantasy land, hyper detailed",
    "EXTRA_TERRESTRIAL": "deepdream cosmic, painting by Android Jones, cosmic entity, humanoid creature, James Jean soft light 4k, sci-fi, extraterrestrial, cinematic",
    "FANTASY": "fantasy matte painting, fantasy landscape, ( ( Thomas Kinkade ) ), whimsical, dreamy, Alice in Wonderland, daydreaming, epic scene, high exposure, highly detailed, Tim White, Michael Whelan",
    "FIREBENDER": "fire elements, fantasy, fire, lava, striking. A majestic composition with fire elements, fire and ashes surrounding, highly detailed and realistic, cinematic lighting",
    "FORESTPUNK": "forestpunk, vibrant, HDRI, organic motifs and pollen in the air, bold vibrant colors and textures, spectacular sparkling rays, photorealistic quality with Hasselblad",
    "FRACTAL": "fractal patterns, fractal geometry, psychedelic mandala, fractal mandala art, fractal patterns, abstract fractal",
    "FRESCO": "fresco painting, wall frescoes, frescoes, from the history, detailed fresco, fresco, renaissance, fresco in a church",
    "FUTIRISTIC CITYSCAPE": "Dominated by blues, silvers, and neon accents like purples, pinks, cyans, Texture Smooth and polished surfaces contrast with gritty, urban elements, There can be high-contrast lighting and reflections, Geometric form, angular, and sometimes asymmetrical shapes, The skyline would be a common motif, A sense of anticipation and excitement, mixed with a feeling of isolation and the unknown",
    "GHOTIC": "goth lifestyle, dark goth, grunge, cinematic photography, dramatic dark scenery, dark ambient beautiful",
    "GLASS_ART": "inside glass ball, translucent sphere, CGSociety 9, glass orb, Behance, polished, beautiful digital artwork, exquisite digital art, in a short round glass vase, Octane Render",
    "GLITCH": "glitch, glitch art, glitched, glitchy, glitch aesthetic, colorful glitched, glitchy, glitching",
    "GRAFFITI": "graffiti background, colorful graffiti, graffiti art style, colorful mural, ravi supa, symbolic mural, juxtapoz, pablo picasso, street art",
    "GREEK_MYTHOLOGY": "Greek mythology, mythology art, Olympus gods, dramatic lighting and intense colors, attention to detail and to the ancient history, ancient Greek myths",
    "GTA": "gta iv art style, gta art, gta loading screen art, gta chinatown art style, gta 5 loading screen poster, grand theft auto 5, grand theft auto video game",
    "HALLOWEEN": "in Halloween style, Halloween, dark, moody, atmospheric, horror art style, Halloween fantasy art, Halloween concept, CGSociety 7, halloween, creepy",
    "HAUNTED": "horror CGI 4k, scary color art in 4k, horror movie cinematography, Insidious, La Llorona, still from animated horror movie, film still from horror movie, haunted, eerie, unsettling, creepy",
    "HQL": "4k, 8k, Ultra Realistic, Extreme detail, Detailed edges, Extreme Quality, Extreme realistic, ULTRA HIGH DEFINITION DETAILS, very detailed, Ultra HD",
    "HQ": "High Quality, 8K, Cinematic Lighting, Stunning background, high detail, realistic, incredible 16k resolution produced in Unreal Engine 5 and Octane Render for background, sunshafts",
    "HISTORICAL": "18th-century French fashion, oil painting, historical figure, in the style of Rococo, based on historical costumes, history, historical, classical",
    "HORROR": "classic horror, classic horror movie style, in a creepy atmosphere, in a horrifying atmosphere, CGSociety 5, horror art style",
    "ICON": "single vector graphics icon, iOS icon, smooth shape, vector",
    "ILLUSTRATION": "minimalistic vector art, illustrative style, style of Ian Hubert, style of Gilles Beloeil, inspired by Hsiao-Ron Cheng, style of Jonathan Solter, style of Alexandre Chaudret, by Echo Chernik",
    "IMPRESSIONISM": "impressionism, impressionist, impressionist painting, post-impressionism, style of impressionism, impressionistic, style of Monet",
    "INK": "Black Ink, Hand drawn, Minimal art, ArtStation, ArtGem, monochrome",
    "INDUSTRIAL": "industrial, digital art, dystopian cityscape, intense color, complex composition, post-industrial, urban",
    "INTERIOR": "modern architecture by Makoto Shinkai, Ilya Kuvshinov, Lois van Baarle, Rossdraws, and Frank Lloyd Wright",
    "JAPANESE": "with Japanese themes, Japan, Japanese woodblock print, ukiyo-e, Japan, Japanese woodblock style, Hiroshige, Hokusai",
    "JUNGLE": "Jungle scene, jungle atmosphere, lush green jungle, jungle landscape, deep in the jungle, realistic jungle, jungle CGSociety 3",
    "KAWAII_CHIBI": "kawaii chibi romance, fantasy, illustration, colorful idyllic cheerful, kawaii chibi inspired",
    "KNOLLING_CASE": "in square glass case, glass cube, glowing, knolling case, Ash Thorp, studio background, Desktopography, CGSociety 9, CGSociety, mind-bending digital art",
    "LANDSCAPE": "landscape, beautiful landscape, stunning landscape, mountainous landscape, beautiful digital landscape, landscape painting, breathtaking landscape, realism",
    "LOGO": "creative logo, unique logo, visual identity, geometric type, graphic design, logotype design, brand identity, vector based, trendy typography, best of Behance",
    "LUMINOUS": "ethereal, glowing, soft light, luminous colors, dreamlike, celestial, radiant, otherworldly, transcendent, mystical, heavenly",
    "MACRO_PHOTOGRAPHY": "macro photography, award winning macro photography, depth of field, extreme closeup, 8k hd, focused",
    "MAGICAL": "magical, magical world, magical realism, magical atmosphere, in a magical world, magical fantasy art",
    "MAGIC EYE": "Stereogram, magic eye, autostereogram, different colors, patterns or dots, 3d rendering, repeating pattern, when viewed with crossed eyes a 3D object should emerge,  when viewed with crossed eyes a 3D object should emerge",
    "MANDALA": "mandala, mandala design, intricate mandala, mandala art, complex mandala, beautiful mandala",
    "MANGA": "manga style, comic book art, black and white ink, dynamic poses, expressive characters, manga panel layout, action-packed scenes",
    "MARBLE": "in greek marble style, classical antiquities, ancient greek classical ancient greek art, marble art, realistic, cinematic",
    "MARBLEIZED": "marble texture, abstract patterns, vibrant colors, fluid and organic shapes, mesmerizing and unique, inspired by marbling techniques, surreal atmosphere",
    "MARVEL": "album art, Poster, layout, typography, logo, risography, Ghibli, Simon Stålenhag, insane detail, ArtStation, 8k",
    "MATISSE": "Matisse, Matisse cutouts, Matisse style, Matisse painting, Henri Matisse, Matisse's",
    "MECHA": "futuristic mech design, robotic, mechanical, cybernetic, sleek and angular, high-tech, mechanical details, sci-fi battle scene, metallic textures",
    "MECHANICAL": "mechanical gears, steampunk, mechanical devices, intricate details, metallic textures, gears and cogs, mechanical clockwork, industrial aesthetic",
    "MEDIEVAL": "movie still from Game of Thrones, powerful fantasy epic, middle ages, lush green landscape, olden times, Roman Empire, 1400 CE, highly detailed background, cinematic lighting, 8k render, high quality, bright colors",
    "METROPOLIS": "urban cityscape, towering skyscrapers, bustling streets, neon lights, futuristic elements, cyberpunk-inspired, dynamic composition",
    "MINECRAFT": "minecraft build, style of minecraft, pixel style, 8 bit, epic, cinematic, screenshot from minecraft, detailed natural lighting, minecraft gameplay, mojang, minecraft mods, minecraft in real life, blocky like minecraft",
    "MINIMALISM": "minimalism, minimalist, minimalist aesthetic, minimalistic style, minimalist art, clean and minimal",
    "MINIMALIST": "minimalist art, minimalistic design, clean lines, simplicity, negative space, minimal color palette, minimalistic composition",
    "MOONLIT": "moonlit scenery, night sky, soft moonlight, stars, tranquil atmosphere, dreamy and ethereal, nocturnal landscape",
    "MOTION_BLUR": "dynamic motion blur, fast movement, blurred lines, sense of speed, energetic composition, action-packed, motion blur effect",
    "MYSTICAL": "fireflies, deep focus, D&D, fantasy, intricate, elegant, highly detailed, digital painting, ArtStation, concept art, matte, sharp focus, illustration, Hearthstrom, Gereg Rutkowski, Alphonse Mucha, Andreas Rocha",
    "MYSTICAL JUNGLE": "Primarily deep greens, bursts of vibrant tropical flower colors like pinks, yellows, and reds, hints of sky blues and dappled sunlight,Texture Rich and detailed, with heavy use of leafy patterns, floral shapes, and animal textures like fur or feathers, Abstract form, organic forms, but sometimes sharply focused to resemble flora or fauna, Invokes a sense of adventure and mystery, with an undercurrent of serenity",
    "MONOCHROME": "black-and-white, monochrome, grayscale, noir, black-and-white photography, monochromatic",
    "NEO_FAUVISM": "neo-fauvism painting, neo-fauvism movement, digital illustration, poster art, CGSociety saturated colors, fauvist",
    "NEON": "neon art style, night time dark with neon colors, blue neon lighting, violet and aqua neon lights, blacklight neon colors, rococo cyber neon lighting",
    "NEO_NOIR": "neo-noir cinematography, dark and moody atmosphere, film noir-inspired lighting, shadows, and high contrast, urban setting, mysterious and atmospheric, cinematic quality",
    "NFT": "NFT art style, NFTs, NFT art, digital NFT, NFT",
    "NIGHTMARE": "nightmarish, nightmare, scary, creepy, unsettling, creepy horror",
    "NORDIC": "Nordic landscapes, serene and tranquil, snowy mountains, fjords, minimalist design, earthy tones, natural beauty",
    "NOSTALGIA": "nostalgic, vintage-inspired, retro colors, old film aesthetic, grainy texture, 80s vibes, sentimental, warm and cozy, reminiscent of childhood",
    "OCEAN": "Ocean scene, under the sea, deep sea, sea creature, ocean landscape, beautiful underwater",
    "OCEANIC": "underwater world, vibrant coral reefs, tropical fish, shimmering water, ethereal lighting, dreamlike and immersive",
    "OLD_WESTERN": "Old Western, Wild West, cowboy era, rustic landscapes, dusty trails, vintage sepia tones, rugged charm",
    "ORIENTAL": "oriental landscape painting, traditional Asian art style, Chinese ink painting, delicate brushwork, tranquil and serene, cherry blossoms, pagodas, and mountains, harmonious color palette",
    "ORIGAMI": "polygonal art, layered paper art, paper origami, wonderful compositions, folded geometry, paper craft, made from paper",
    "PAPERCUT_STYLE": "layered paper art, paper modeling art, paper craft, paper art, papercraft, paper cutout, paper cut out collage artwork, paper cut art",
    "PAINTING": "atmospheric dreamscape painting, by Mac Conner, vibrant gouache painting scenery, vibrant painting, vivid painting, a beautiful painting, dream scenery art, Instagram art, psychedelic painting, lo-fi art, bright art",
    "PALETTE_KNIFE": "detailed impasto brush strokes, detail acrylic palette knife, thick impasto technique, palette knife, vibrant 8k colors",
    "PASTEL DREAM": "pastel colors, dreamy atmosphere, soft and gentle, whimsical, fantasy world, delicate brushstrokes, light and airy, tranquil, serene, peaceful, nostalgic",
    "PASTEL PAINTING": "pastel painting, cinematic lighting",
    "PHOTO REALISTIC": "realistic image, realistic shadows, realistic dramatic lighting, Photo Realistic, 4k, 8k, high resolution, highly detailed, ultra-detailed image, subject focussed, natural beauty, extremely detailed realistic background",
    "PICASO": "painting, by Pablo Picasso, cubism",
    "PIXEL": "pixel art, pixelated, pixel-style, 8-bit style, pixel game, pixel",
    "PIXEL_HORROR": "pixel horror game, pixel horror, horror pixel, scary pixel, horror game pixel art, 8-bit horror",
    "PIXIE_DUST": "pixie dust, fairy dust, magical, shimmering, glowing, sparkling, ethereal",
    "POLAROID": "old polaroid, 35mm",
    "POLY_ART": "low poly, ArtStation, studio lighting, stainless steel, grey color scheme",
    "POP_ART": "Pop art, Roy Lichtenstein, Andy Warhol, pop art style, comic book, pop",
    "POSTER_ART": "album art, Poster, layout, typography, logo, risography, Ghibli, Simon Stålenhag, insane detail, ArtStation, 8k",
    "POST_APOCALYPTIC": "post-apocalyptic landscape, post-apocalyptic, dystopian, end of the world, post-apocalypse, wasteland",
    "PRIMITIVE": "prehistoric cave painting, cave art, ancient art, primitive style, tribal, caveman",
    "PRODUCT_PHOTOGRAPHY": "product photo studio lighting, high detail product photo, product photography, commercial product photography, realistic, light, 8k, award winning product photography, professional closeup",
    "RAINFOREST": "intricate rainbow environment, rainbow bg, from lorax movie, pixar color palette, volumetric rainbow lighting, gorgeous digital painting, 8k cinematic",
    "REALISTIC": "realistic image, realistic shadows, realistic dramatic lighting, 4k, 8k, high resolution, highly detailed, ultra-detailed image, subject focussed, natural beauty, extremely detailed realistic background",
    "RENDER": "isometric, polaroid Octane Render, 3D render 1.5 0 mm lens, KeyShot product render, rendered, KeyShot product render Pinterest, 3D product render, 3D CGI render, 3D CGI render, ultra wide-angle isometric view",
    "RENAISSANCE": "Renaissance period, neo-classical painting, Italian Renaissance workshop, pittura metafisica, Raphael high Renaissance, ancient Roman painting, Michelangelo painting, Leonardo da Vinci, Italian Renaissance architecture",
    "RETRO": "retro futuristic illustration, featured on Illustrationx, Art Deco illustration, beautiful retro art, stylized digital illustration, highly detailed vector art, Mads Berg, automotive design art, epic smooth illustration, by Mads Berg, stylized illustration, Ash Thorp Khyzyl Saleem, clean vector art",
    "RETROWAVE": "Illustration, retrowave art, neon light, retro, digital art, trending on ArtStation",
    "ROCOCO": "François Boucher oil painting, rococo style, rococo lifestyle, a Flemish Baroque, by Karel Dujardin, vintage look, cinematic hazy lighting",
    "ROMANTIC": "romantic scene, romantic atmosphere, romantic style, romance, love, affection",
    "SALVADOR_DALI": "Painting, by Salvador Dali, allegory, surrealism, religious art, genre painting, portrait, painter, still life",
    "SAMURAI": "samurai lifestyle, Miyamoto Musashi, Japanese art, ancient Japanese samurai, feudal Japan art, feudal Japan art",
    "SCATTER": "breaking pieces, exploding pieces, shattering pieces, disintegration, contemporary digital art, inspired by Dan Hillier, inspired by Igor Morski, dramatic digital art, Behance art, CGSociety 9, 3D advanced digital art, mind-bending digital art, disintegrating",
    "SCIFI": "science fiction, futuristic, alien planet, space, otherworldly, cosmic",
    "SHAMROCK_FANTASY": "shamrock fantasy, fantasy, vivid colors, grapevine, celtic fantasy art, lucky clovers, dreamlike atmosphere, captivating details, soft light and vivid colors",
    "SILHOUETTE": "silhouette, dark figure, silhouette against the sunset, shadowy, outline, figure",
    "SKETCH": "pencil, hand drawn, sketch, on paper",
    "SPLATTER": "paint splatter, splatter, splattered, paint splash, colorful splatter, ink splatter",
    "SURREALISM": "salvador dali painting, highly detailed surrealist art, surrealist conceptual art, masterpiece surrealism, surreal architecture, surrealistic digital artwork, whimsical surrealism, bizarre art",
    "STAINED_GLASS": "intricate wiccan spectrum, stained glass art, vividly beautiful colors, beautiful stained glass window, colorful image, intricate stained glass triptych, gothic stained glass style, stained glass window!!!",
    "THE 1990s": "Technology - Desktop computers, bulky CRT televisions, portable CD players, the early internet, or videogame consoles like the Game Boy or PlayStation, Fashion - High-waisted jeans, bright neon colors, plaid flannel shirts, snapback hats, or the grunge look, Entertainment - Influential 90s movies or TV series like Friends or The Matrix, popular toys like Beanie Babies or Tamagotchis, or recognizable music like Britney Spears or Nirvana, Social Events - Major events like the fall of the Berlin Wall, the Y2K scare, or the rise of hip-hop culture",
    "STICKER": "sticker, sticker art, symmetrical sticker design, sticker - art, sticker illustration, die - cut sticker",
    "SUPER HERO": "Super Hero, Super hero tv series, Super hero comic books, super hero outfit, super hero suit, very detailed, bright colors, realistic, dynamic lighting, bold background, detailed background.",
    "TECHNO_ORGANIC": "fusion of technology and nature, futuristic organic forms, biomechanical elements, cybernetic landscapes, harmonious blend",
    "TRIBAL": "tribal art, indigenous culture, intricate patterns, earthy tones, spiritual symbols, tribal masks, primitive aesthetics, cultural heritage",
    "TRIPPY": "psychedelic, trippy, hallucinogenic, LSD-inspired, psychedelic art, 60s psychedelia",
    "TROPICAL": "tropical, tropical landscape, tropical beach, paradise, tropical paradise, vibrant colors",
    "UNDERGROUND": "underground subculture, street art, graffiti, rebellious spirit, gritty and raw, urban energy",
    "UNDERWATER": "underwater scene, oceanic environment, vibrant marine life, coral reefs, deep-sea creatures, ethereal lighting, tranquility and serenity, blues and greens, exploration and mystery",
    "URBAN": "urban landscape, city life, street photography, gritty and raw, graffiti-covered walls, bustling streets, urban decay, metropolitan vibes",
    "URBAN_GRAFFITI": "urban graffiti art, street culture, vibrant tags and murals, rebellious expression, urban decay",
    "VAN_GOGH": "painting, by Van Gogh",
    "VAPORWAVE": "vaporwave aesthetic, nostalgic and glitchy, 80s and 90s pop culture references, pastel colors, retro digital graphics",
    "VECTOR": "vector, vector art, clean lines, bold colors, digital art, graphic design",
    "VICTORIAN": "Victorian, 19th century, period piece, antique, vintage, historical",
    "VIBRAN_VIKING": "Viking era, digital painting, pop of color, forest, paint splatter, flowing colors, background of lush forest and earthy tones, artistic representation of movement and atmosphere",
    "VIBRANT": "Psychedelic, watercolor spots, vibrant color scheme, highly detailed, romanticism style, cinematic, ArtStation, Greg Rutkowski",
    "VINTAGE": "vintage, retro, old-fashioned, nostalgic, antique, classic",
    "VINTAGE_PHOTO": "vintage photography, old film grain, sepia tones, faded colors, nostalgic scenes, evocative and timeless",
    "WARHOL": "Warhol-inspired pop art, bold and repetitive imagery, bright color blocks, celebrity culture",
    "WATERBENDER": "water elements, fantasy, water, exotic, a majestic composition with water elements, waterfall, lush moss and exotic flowers, highly detailed and realistic, dynamic lighting",
    "WILDLIFE": "wildlife photography, capturing animals in their natural habitats, close-ups of animals, biodiversity and nature, vibrant colors and textures, endangered species, conservation",
    "WINTER_WONDERLAND": "winter landscape, snowy scenes, frosty atmosphere, icy blues, serene and magical",
    "WOOLITIZE": "cute! C4D, made out of wool, volumetric wool felting, wool felting art, Houdini SideFX, rendered in Arnold, soft smooth lighting, soft pastel colors",
    "WESTERN": "western, wild west, cowboy, American frontier, rustic, vintage",
    "WITCHY": "witch, witchy, magical, dark, mystical, pagan",
    "WOODCUT": "woodcut, linocut, engraving, woodblock print, old-fashioned, traditional",
    "ZEN": "Zen-inspired art, minimalist and tranquil, Japanese Zen gardens, simplicity and balance, meditative and serene, calming color palette, empty space and minimal details",
    "ZENTANGLE": "zentangle, zentangle pattern, intricate zentangle, zentangle design, doodle, zentangle art"
}

async def fetch_generated_image(generation_id):
    for _ in range(240):
        await asyncio.sleep(1)
        response = requests.get(f'http://localhost:8000/check_status/{generation_id}', verify=False)  # < ---- set your server URL and Port
        print(f"Attempt {_}: Response from FastAPI: {response.text}")
        if response.status_code == 200:
            data_response = response.json()
            image_urls = data_response.get('image_urls', [])
            if image_urls:
                print(f"Returning {len(image_urls)} image URLs")
                return [{"url": url, "id": idx} for idx, url in enumerate(image_urls)]
    return None


@bot.command()
async def generate(ctx, *, user_input: str):
    if ctx.channel.id != channel_input_id:
        return 
    """
    Generate an image based on the provided user input and optional parameters.
    Parameters:
    user_input: The entire input string from the user.
    """

    # Default parameters
    data = {
        'prompt': user_input,
        'modelId': '6bef9f1b-29cb-40c7-b9df-32b51c1f67d3', # <---- put your model ID here
        'width': 768,
        'height': 768,
        "sd_version": "v2",        
        'promptMagic': True,  
        'highContrast': True, 
        "alchemy": True,
        "contrastRatio": 0.5,
        "expandedDomain": True,
        "highResolution": False,
        "presetStyle": "DYNAMIC",
        "promptMagicVersion": "v3",
        "num_images": 4,                                                           
    }

    # If the user does not provide a style, add High quality Lighting as the default style
    if "--s" not in user_input:
        if "--ar" in user_input:
            # Split the user input at '--ar' and insert '--s HQL' before it
            parts = user_input.split("--ar")
            user_input = parts[0].strip() + " --s HQL --ar" + parts[1].strip()
        else:
            user_input += " --s HQL"    

    # Extracting parameters from user input and updating the default values
    if "--ar" in user_input:
        aspect_ratio = user_input.split("--ar")[1].split()[0].lower()  # Convert to lowercase for case insensitivity
        if aspect_ratio == "16:9":
            data['width'], data['height'] = 912, 512
        elif aspect_ratio == "1:1":
            data['width'], data['height'] = 768, 768
        user_input = user_input.replace(f"--ar {aspect_ratio}", "").strip()

    # Extracting style descriptions from user input
    if "--s" in user_input:
        style_code = user_input.split("--s")[1].split()[0].upper()
        if style_code in style_descriptions:
            user_input = f"{user_input}, {style_descriptions[style_code]}"
        user_input = user_input.replace(f" {style_code}", "").strip()
        
    # Remove '--s' from the user input
    user_input = user_input.replace("--s", "").strip()  

    # Update the prompt in the data dictionary
    data['prompt'] = user_input
    
    # Here, after processing the user input, send the notification message:
    embed = discord.Embed(description=f"'{user_input}' - added to the Queue, please be patient, Depending on server load, Generation takes anywhere from 20 seconds to 2 mins.", color=0x0000ff)  # 0x0000ff is blue
    await ctx.send(embed=embed)    

    # Serialize the entire data dictionary
    serialized_data = json.dumps(data)

    # Debugging: Print the serialized data before sending
    print("Serialized Data to be sent:", serialized_data)

    # Fetch the desired channel
    target_channel = bot.get_channel(CHANNEL_ID)

    # Make the AJAX request
    response = requests.post('http://localhost:8000/generate_image/', json=data, verify=False) # < ---- set your server URL and Port

    # Check if the response was successful before processing it
    if response.status_code == 200:
        data_response = response.json()
        print(f"Response from FastAPI: {data_response}")
    
    if 'sdGenerationJob' in data_response:
        generation_id = data_response['sdGenerationJob']['generationId']

        
        outputs = await fetch_generated_image(generation_id)
        print(f"Received {len(outputs if outputs else [])} image URLs from fetch_generated_image")
        if outputs:
            num_images = len(outputs)
            if num_images == 1:
                await target_channel.send("Image Generated with Leonardo model:")
            else:
                await target_channel.send(f"{num_images} Images Generated with Leonardo model:")
        
            for output in outputs:
                image_url = output['url']
                # Fetch the image and send as attachment
                image_response = requests.get(image_url, verify=False)
                if image_response.status_code == 200:
                    image_data = io.BytesIO(image_response.content)
                    await target_channel.send(file=discord.File(image_data, f"generated_image_{output['id']}.jpg"))
                else:
                    await target_channel.send(f"Error fetching the generated image from URL: {image_url}")
        else:
            await target_channel.send("Error: Image generation took too long or encountered an error.")




# If you have code that requires SSL certificates, you can access them with args.ssl_keyfile and args.ssl_certfile

bot.run(TOKEN)
