from PIL import Image
import random, sys

def quick_sort(pixels):
    #Quicksort function that sorts pixels based on combined RGB values (R + B + G)
    if pixels == []:
        return pixels

    else:
        pivot = pixels[0]
        lesser = quick_sort([x for x in pixels[1:] if (x[0] + x[1] + x[2]) < (pivot[0] + pivot[1] + pivot[2])])
        greater = quick_sort([x for x in pixels[1:] if (x[0] + x[1] + x[2]) >= (pivot[0] + pivot[1] + pivot[2])])
        return lesser + [pivot] + greater

def sort_all_pixels(img):
    #sorts every line of pixels
    #print("Sorting all pixels.")

    #print("Opening image...")
    img = img.convert('RGBA')
    #print("Get data...")
    data = img.load()

    new = Image.new('RGBA', img.size)

    pixels = []
    sorted_pixels = []
    #print("Getting pixels...")
    #Load all of the pixels into the pixels list
    for y in range(img.size[1]):
        pixels.append([])
        for x in range(img.size[0]):
            pixels[y].append(data[x, y])

    for y in range(img.size[1]):
            sorted_pixels.append(quick_sort(pixels[y]))

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            new.putpixel((x, y), sorted_pixels[y][x]) #apply the pixels to the new image

    return new


def random_sort_pixels(img, intensity):
    #sorts pixels in a random fashion

    if intensity > 100:
        intensity = 100

    #Open the image, convert it to RGBA, get the pixels
    img = img.convert('RGBA')
    data = img.load()

    new = Image.new('RGBA', img.size)

    pixels = []
    sorted_pixels = []

    #Load all of the pixels into the pixels list
    for y in range(img.size[1]):
        pixels.append([])
        for x in range(img.size[0]):
            pixels[y].append(data[x, y])


    for y in range(img.size[1]):
        #pick different starting points for each line
        if(random.randint(0, 100) > intensity):
            sorted_pixels.append(pixels[y]) #Don't sort this line of pixels
        else:
            minsort = random.randint(3, len(pixels[y]) - 3) #pick the start of the sorted area on this pixel line
            maxsort = random.randint(minsort, len(pixels[y]) - 1)# pick the end of the sorted area on this pixel line
            sort = []
            for x in range(minsort, maxsort):
                sort.append(pixels[y][x])

            sort = quick_sort(sort) #sort the pixels by brightness

            i = 0
            for x in range(minsort, maxsort):
                pixels[y][x] = sort[i]
                i = i + 1

            sorted_pixels.append(pixels[y])

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            new.putpixel((x, y), sorted_pixels[y][x]) #apply the pixels to the new image

    return new

def sort_pixels_pivot(img):
    #print ("Sorting pixels on pivot.")

    #Open the image, convert it to RGBA, get the pixels
    img = img.convert('RGBA')
    data = img.load()

    new = Image.new('RGBA', img.size)

    pixels = []
    sorted_pixels = []

    #Load all of the pixels into the pixels list
    for y in range(img.size[1]):
        pixels.append([])
        for x in range(img.size[0]):
            pixels[y].append(data[x, y])


    minsort = random.randint(3, img.size[0] - 3) #get sorting pivot
    for y in range(img.size[1]):
        maxsort = random.randint(minsort, len(pixels[y]) - 1) #pick the end of the sorted area on this pixel line
        sort = []
        for x in range(minsort, maxsort):
            sort.append(pixels[y][x])
        sort = quick_sort(sort) #sort the pixels by brightness

        i = 0
        for x in range(minsort, maxsort):
            pixels[y][x] = sort[i]
            i = i + 1

        sorted_pixels.append(pixels[y])

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            new.putpixel((x, y), sorted_pixels[y][x]) #apply the pixels to the new image

    return new

# sys.setrecursionlimit(10000) #Increase the recursion depth limit. Without this, the script fails on larger images because quicksort recurses too much.
# sort_all_pixels("image.jpg")
# random_sort_pixels("image.jpg", random.randint(1, 100))
# sort_pixels_pivot("image.jpg")
