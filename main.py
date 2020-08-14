import math
from PIL import Image
from os import listdir, remove, mkdir
from os.path import isfile, isdir, join
from datetime import datetime


# 2nd Rework
# Have to convert this from hardcoded numbers to % of size of the image
# Generated Card Size: 1500 x 2092 (400% export settings in MSE)
# Bleed Image Size: 1651 x 2243
# To add 10% Bleed allowance

#def ToMPC(image_path):
#    frame = Image.open(image_path)
#    bleed = Image.open('./scripts/MPCFormatter/resources/bleed.png')
#
#    bleed.paste(frame, (75,75))
#    bleed = cover_corner(bleed, 75, 75)
#    bleed = cover_corner(bleed, 1527, 75)
#    bleed = cover_corner(bleed, 75, 2107)
#    bleed = cover_corner(bleed, 1523, 2119)
#
#    out_path = image_path.replace(".png", "_mpc.png")
#    bleed.save(out_path)
#
#    return out_path
#
#def cover_corner(image, xC, yC):
#    black = Image.new('RGB', (60,60), "black")
#    image.paste(black, (xC,yC))
#    return image


# 3rd Rework: Time to make it work for various different sizes but right this time
# The typical magic card is 63mm x 88mm
# MPC recommends a further 1/8" (3.175mm) on each side of the image to allow for bleed
# MPC recommends an additional 1/8" inside for bleed, but this is okay since we use black borders
# So essentially if we take the standard 63mm x 88mm of a magic card and add 3.175 to each side we get 
# 69.35 x 94.35
# Taking the 6.35mm we added to the 63mm, we can find that we are effectively adding 10% width
# However what I failed to see in the previous attmept is that we are only adding 7.2% height
# Also want to add support for other colored borders


# I'm trying snake_case for this so my linter will stop yelling at me :<
def main():
    now = datetime.now()
    in_path = "./resources/in/"
    out_folder = "./resources/out/"
    out_path = "./resources/out/" + now.strftime("%Y-%m-%d") + "/"

    if not isdir(in_path):
        mkdir(in_path)

    if not isdir(out_folder):
        mkdir(out_folder)

    if not isdir(out_path):
        mkdir(out_path)

    files = [f for f in listdir(in_path) if isfile(join(in_path, f))]
    numCount = 0

    for my_file in files:
        to_mpc(in_path + my_file, my_file, out_path)
        numCount += 1
    
    print("Successfully processed %i files..." % (numCount))

def to_mpc(image_path, image_name, out_path):
    frame = Image.open(image_path)
    bleed = Image.open('./resources/bleed.png')
    # Percentage to account for bleed. 1.10 = 10%
    horiz_bleed_acct = 1.100
    verti_bleed_acct = 1.072
    rect_acct = 0.0363
    horiz_acct = 0.0454
    verti_acct = 0.0326

    card_x, card_y = frame.size
    new_bleed = bleed.resize((round_half_up(card_x * horiz_bleed_acct), round_half_up(card_y * verti_bleed_acct)))
    total_x, total_y = new_bleed.size

    #edgeAllowX = round_half_up(round_half_up(total_x - card_x) / 2)
    #edgeAllowY = round_half_up(round_half_up(total_y - card_y) / 2)

    # rect_dim? It damn near killed em!
    rect_dim_x = round_half_up(total_x * rect_acct)
    rect_dim_y = round_half_up(total_y * rect_acct)
    horiz_left_x = round_half_up(total_x * horiz_acct)
    horiz_right_x = total_x - (horiz_left_x + rect_dim_x)
    verti_top_y = round_half_up(total_y * verti_acct)
    verti_bot_y = total_y - (verti_top_y + rect_dim_y)

    new_bleed.paste(frame, (horiz_left_x, verti_top_y))
    new_bleed = cover_corner(new_bleed, horiz_left_x, verti_top_y, rect_dim_x, rect_dim_y) # cover top left corner
    new_bleed = cover_corner(new_bleed, horiz_right_x, verti_top_y, rect_dim_x, rect_dim_y) # cover top right corner
    new_bleed = cover_corner(new_bleed, horiz_left_x, verti_bot_y, rect_dim_x, rect_dim_y) # cover bottom left corner
    new_bleed = cover_corner(new_bleed, horiz_right_x, verti_bot_y, rect_dim_x, rect_dim_y) # cover bottom right corner
    
    # logic from my portolio site's version of this
    # out_path = image_path.replace(".png", "_mpc.png")
    # bleed.save(out_path)

    new_image_name = image_name.replace(".png", "_mpc.png")
    new_image_name = new_image_name.replace(" ", "_")
    new_bleed.save(out_path + new_image_name)
    remove(image_path)

def cover_corner(image, x_c, y_c, rect_size_x, rect_size_y):
    black = Image.new('RGB', (rect_size_x, rect_size_y), "black")
    image.paste(black, (x_c, y_c))
    return image


def round_half_up(myNum, decimal=0):
    multiplier = 10 ** decimal
    return int(math.floor(myNum * multiplier + 0.5) / multiplier)

main()
