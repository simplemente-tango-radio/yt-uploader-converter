from PIL import Image, ImageFilter
import os
import subprocess
import time
import sys

song_list = []

RED   = "\u001b[31m"
BLUE  = "\u001b[34m"
CYAN  = "\u001b[36m"
YELLOW = "\u001b[33m"
GREEN = "\u001b[32m"
MAGENTA = "\u001b[35m"
RESET = "\u001b[0m"

PROGRAM_DESC = '"Simplemente Tango" programa de tango fundado el 1º de Julio de 1996, con la conducción de Jorge Alarcón, de Lúnes a Viernes de 14 a 15 hs por Radio Gualeguay (AM 1520) - www.radiogualeguay.com.ar\n'

BIO = 'Compositor y bandoneonista argentino. Fue uno de los artífices de la renovación del tango, sobre todo a partir de 1955, año en que regresó a Argentina después de un período de estudios en París bajo la dirección de Nadia Boulanger, célebre pedagoga que le aconsejó no olvidar nunca la música popular, precepto que el músico tuvo siempre presente. Decarissimo, Milonga del ángel, La muerte del ángel, Invierno porteño, Buenos Aires hora cero, Balada para un loco y Adiós, Nonino son algunos de sus tangos más populares. En ellos conviven el género tradicional, la música clásica y el jazz y entremezclan sus lenguajes, técnicas y estilos, lo que les confiere un aspecto novedoso y de un considerable atractivo, a pesar de lo cual despertaron el rechazo de los círculos tanguísticos más conservadores. A Piazzolla se le debe también un valioso Concierto para bandoneón y orquesta, importante por todo lo que supone de reivindicación de este instrumento, más allá del papel de acompañamiento en conjuntos de baile, y una ópera, María de Buenos Aires (1968).\n'

def newCover(coverpath, maskpath, output):
    #4k 3840 x 2160
    kwidth = 3840
    kheight = 2160

    mask = Image.open(maskpath)
    or_cover = Image.open(coverpath)
    cover = or_cover.resize((kwidth, kheight), Image.ANTIALIAS)
    canvas = Image.new(mode="RGB", size=(3840, 2160))
    canvas.paste(cover)

    blurpath = canvas.filter(ImageFilter.GaussianBlur(15))
    blurpath.paste(mask, (0, 0), mask)

    orcover_w, orcover_h = or_cover.size

    offset = ((3840 - orcover_w) // 2, (kheight - orcover_h) // 2)
    blurpath.paste(or_cover, offset)
    blurpath.save(output)
def compileVideo(cover, audio):
    result = subprocess.run(['ffmpeg', '-loop','1', '-i',cover, '-i',audio, '-c:v','libx264', '-tune','stillimage', '-c:a','aac', '-b:a','192k', '-pix_fmt','yuv420p','-threads','0', '-shortest',audio+'.mp4'], stdout=subprocess.PIPE)
def getAlbumList():
    result = subprocess.run(['ls', '-l'], stdout=subprocess.PIPE)
    dir_list = result.stdout.splitlines()
    for file in dir_list:
        if b'.flac' in file and b'.mp4' not in file:
            file_e = str(file).split(':')
            song = file_e[1]
            song = song[3:len(song)]
            #song = song.replace(' ','\ ')
            song = song.replace("'","")
            song = song.replace('"','')
            #song = song.replace(")",'\(')
            #song = song.replace("(",'\)')
            song_list.insert(len(song_list), song)
def returnCorrectValue(line,key):
    line = line.split(':')
    value = line[1].strip()
    obj = "%s: %s" % (key,value)
    return obj
def audioInfo(file):
    cabecera = []
    audio_info = []
    artist = ''
    keywords = []
    song = ''
    result = subprocess.run(['mediainfo','--full',file], stdout=subprocess.PIPE)
    audioInfo = result.stdout.splitlines()
    for line in audioInfo:
        line = line.decode("utf-8")
        if 'Performer' in line and 'Performer' not in cabecera:
            cabecera.insert(len(cabecera), returnCorrectValue(line,'Performer'))
        if 'Album' in line and 'Album' not in cabecera:
            cabecera.insert(len(cabecera), returnCorrectValue(line,'Album'))
        if 'Recorded date' in line and 'Recorded date' not in cabecera:
            cabecera.insert(len(cabecera), returnCorrectValue(line,'Recorded date'))
        if 'Copyright' in line and 'Copyright' not in cabecera:
            cabecera.insert(len(cabecera), returnCorrectValue(line,'Copyright'))
        if 'ISRC' in line and 'ISRC' not in cabecera:
            cabecera.insert(len(cabecera), returnCorrectValue(line,'ISRC'))
        #audioinfo
        if 'Format/Info' in line and 'Format/Info' not in audio_info:
            audio_info.insert(len(audio_info), returnCorrectValue(line,'Format/Info'))
        if 'Overall bit rate mode' in line and 'Overall bit rate mode' not in audio_info:
            audio_info.insert(len(audio_info), returnCorrectValue(line,'Overall bit rate mode'))
        if 'Overall bit rate' in line and 'Overall bit rate' not in audio_info and 'kb' in line:
            audio_info.insert(len(audio_info), returnCorrectValue(line,'Overall bit rate'))
        if 'Channel(s)' in line and 'Channel(s)' not in audio_info and 'channel' in line:
            audio_info.insert(len(audio_info), returnCorrectValue(line,'Channel(s)'))
        if 'Channel layout' in line and 'Channel layout' not in audio_info:
            audio_info.insert(len(audio_info), returnCorrectValue(line,'Channel layout'))
        if 'Channel positions' in line and 'Channel positions' not in audio_info:
            audio_info.insert(len(audio_info), returnCorrectValue(line,'Channel positions'))
        if 'Sampling rate' in line and 'Sampling rate' not in audio_info and 'kHz' in line:
            audio_info.insert(len(audio_info), returnCorrectValue(line,'Sampling rate'))
        if 'Samples count' in line and 'Samples count' not in audio_info:
            audio_info.insert(len(audio_info), returnCorrectValue(line,'Samples count'))
        if 'Bit depth' in line and 'Bit depth' not in audio_info and 'bits' in line:
            audio_info.insert(len(audio_info), returnCorrectValue(line,'Bit depth'))
        if 'Compression mode' in line and 'Compression mode' not in audio_info:
            audio_info.insert(len(audio_info), returnCorrectValue(line,'Compression mode'))
        if 'Writing library' in line and 'Writing library' not in audio_info:
            audio_info.insert(len(audio_info), returnCorrectValue(line,'Writing library'))
        if 'Complete name' in line:
            line = line.split(':')
            line = line[1].split('.')
            line = line[0].split('-')
            artist = line[1]
            song = "[%s] %s" % (line[0],line[2])
    keywords.insert(len(keywords),cabecera[0].split(':')[1])
    keywords.insert(len(keywords),cabecera[1].split(':')[1])
    keywords.insert(len(keywords),song)
    album = keywords[0]
    return cabecera,audio_info,artist,album,song,keywords


newCover("cover.jpg","mask.png","yt_video_img.jpg")
time.sleep(1)
getAlbumList()

for song in song_list:
    compileVideo("yt_video_img.jpg", song)
    nfo = audioInfo(song)
    cabecera = nfo[0]
    audio_info = nfo[1]
    artist = nfo[2]
    album = nfo[3]
    pieza = nfo[4]
    keywords = nfo[5]
    title = "%s - %s - %s" % (artist,album,pieza)
    sys.stdout.write(GREEN)
    print("UPLOADING: %s" % title)
    sys.stdout.write(RESET)
    description = ''
    for line in cabecera:
        description += line+'\n'
    description += '\n'+BIO
    description += '\n'+PROGRAM_DESC
    description += '\n'+'#AUDIO INFO:'+'\n'
    for audioline in audio_info:
        description += audioline+'\n'
    result = subprocess.run(['python3', 'upload_video.py', '--file='+song+'.mp4', '--title='+title, '--description='+description, '--keywords=', '--category=10', '--privacyStatus=public'], stdout=subprocess.PIPE)
    sys.stdout.write(CYAN)
    print(result)
    sys.stdout.write(RESET)
    exit()
