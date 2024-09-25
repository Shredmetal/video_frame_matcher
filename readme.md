# Frame Finder

A quick tool to find the exact episode and timestamp of a frame in a video.

Garbage collects every 1,000 frames it processes. It might take a while to get through a pile of videos because it checks every frame.

## Features
- Select target image
- Choose directory of videos to search
- Choose directory to write matched frames to
- Adjust similarity threshold
- Displays matches with video filename and timestamp and logs

## Usage
1. Run the executable
2. Select your image
3. Choose the directory your videos
4. Choose where to write matched frames to
5. Set similarity threshold (default: 5)
6. Set Number of Processes (Recommended: Half the number of threads your CPU has, if you run into errors, reduce this)
7. Click "Search!"
8. View results in the popup window

Created for a friend to locate the source of their Pokemon animation cel. Enjoy!

[Instructional Video](https://youtu.be/AqENqn29Zyk)

## Notes

The issue with animation cels is that the comparison will never be perfect. You MUST use scans of the cel and NOT a photo.

In the secondary market cels sold may not have all the cel layers as per the original shot.

The backgrounds may not be original, or be from a slightly different scene, or be missing. This makes it MUCH harder to find the shot.

But that said, having close matches to search from in the write directory should make things quicker than watching the whole thing.

## Threshold Settings Examples:

Setting a higher threshold will pick out slightly different things, this one was at threshold 15 and is wrong: 

![threshold_15](https://github.com/user-attachments/assets/60ba1d5a-2d5c-4990-ac44-3ab1a75a13ec)

However, this was at threshold 18 and it picked out the correct Ash and Pikachu, but the cel owner did not have the rest of the cel layers:

![threshold_18](https://github.com/user-attachments/assets/f33c66cf-b7f1-4d67-8a79-5522c170b8bc)

If you're hunting cels rather than stills from a video, happy hunting!

