from __future__ import division
from PIL import Image
import PixelProcess

debug = 0


class Merger:

    def __init__(self, outfile):
        """
        `Author`: Bill Clark

        A merger is a class that allows for a number of images to merged sequentially. It is designed to
        merge each image incrementally, outputting to an outfile when requested. There are a variety of
        ways to preform the merges for different circumstance. The class contains an autosave feature that
        will save the image after each merge, which is defaulted to off. There is also a contained PixelChecker
        and PixelActor, which define how the merges process.
        Merger works off an internal state. Each merge operation (irrelevant of number merged in that operation)
        changes the state of the output data. Merge and MergeAs change the state permanently. ExportMerge and
        TestMerge do not change the state of the output data.

        `outfile`: The file address to save the output to.
        """

        self.initialized = 0
        self.autoSave = 0

        self.outfile = outfile

        self.processor = PixelProcess.PixelRemote()
        self.mergedFiles = []

    def setup(self, file):
        """
        `Author`: Bill Clark

        This method is called if a merge is activated and no prior merges have been done. It sets the image to
        be merged as the output result, as nothing cannot be merged with an image object. This method is
        internal and does not need to be called by a user. It is called if necessary from the merge methods.

        `file`: A path to an image to initialize the Merge with.
        """
        self.outimage = Image.open(file)
        self.processor.outdata = self.outimage.load()
        if self.autoSave: self.save()
        self.initialized = 1

    def merge(self, *images):
        """
        `Author`: Bill Clark

        The main merge method. All other variants actually call this merge at some point in execution. The
        method calls setup if no merges have been done prior so that merges can be done against the first.
        This uses the checkandact method to operate on each image given to it. That method covers all the
        actual pixel processing.
        When debug is enabled, merge prints the percentage of different and same pixels.

        `images`: Any number of image paths to merge together.
        """

        if not self.initialized:
            self.setup(images[0])
            images = images[1:]

        if len(images) > 0:
            for image in images:
                changed = self.checkAndAct(image)

            self.mergedFiles.append(image)
            if debug: self.printDiffSame(changed)
            if debug: self.show()

        if self.autoSave: self.save()
        
    def testMerge(self, *images):
        """
        `Author`: Bill Clark

        A test merge is a merge that doesn't save state. Each call to merge changes the internal data.
        In the case a user wants to see the result of a merge without modifying the data, test merge will
        do the job. Test merge is actually a call to exportmerge taking advantage of it's outfile variable.

        `images`: Any number of image paths to be merged.
        """

        self.exportMerge(None, *images)

    def exportMerge(self, outfile, *images):
        """
        `Author`: Bill Clark

        Export merge is a merge operation that does not change state. Unlike TestMerge, this merge will
        write the temporary image to a given outfile. If the outfile is None, export will not write anything.
        This side effect is how TestMerge works. Export merge turns off the autosave feature to be sure that
        doesn't modify the main output file.

        `images`: the image paths to be merged.

        `outfile`: Where to set the new output path to.
        """

        # Make a backup of the outimage if one has been initialized.
        orig = None
        if self.initialized: orig = self.outimage.copy()

        # Saves the autosave state and merges.
        state = self.autoSave
        self.autoSave = 0
        self.merge(*images)
        self.autoSave = state

        # If the outfile is None, show the image and continue. If an outfile exists, save the image instead.
        if outfile is not None: self.save(self.outimage, outfile)
        else:  self.show()

        # If the back up was made, restore the status to before the last merge. Else, reset the object.
        if orig is not None:
            self.outimage = orig
            self.processor.outdata = self.outimage.load()
        else:
            self = Merger(self.outfile)

    def mergeAs(self, outfile, *images):
        """
        `Author`: Bill Clark

        This is a variant of the main merge method. It changes the outfile permanently, functioning like
        a save as option. Otherwise it differs completely to merge.

        `images`: the image paths to be merged.

        `outfile`: Where to set the new output path to.
        """

        self.outfile = outfile
        self.merge(*images)

    def checkAndAct(self, img):
        """
        `Author`: Bill Clark

        The primary action method. This method takes an image and merges it onto the output data stored
        in the class. For every pixel in each image, the class's pixelChecker is used to compare them.
        If the check returns true, the class's pixelActor is called to act on the pixels. For every acted on
        pixel pair, the method's counter is increased. This count is returned as a statistic.

        `img`: An image file to be merged onto the class's image.

        `return`: The number of modified pixels.
        """
        compareimage = Image.open(img)
        self.processor.comparedata = compareimage.load()

        counter = 0
        print self.outimage.size
        for y in range(self.outimage.size[1]):
            for x in range(self.outimage.size[0]):
                counter += self.processor.run(x, y, x, y)
        return counter

    def convert(self, *images):
        """
        `Author`: Bill Clark

        This method converts any number of given images to RGBA color format. Pixel comparision is done via
        the rgb values, and requires the images to be in that format. The converted files are saved to
        a Converts folder as to not fill ones input folder with temporary files.

        `images`: The images that need to be converted.

        `return`: A list of file paths leading to the convert images, which can passed to further methods.
        """
        ret = []
        count = 0
        for image in images:
            img = Image.open(image)
            im = img.convert("RGBA")

            split = image.split('/')
            path = '/'.join(split[:-1]) + '/Converts/' + ''.join(split[-1:])

            ret.append(path)
            im.save(path)
            count += 1
        return ret

    def show(self, image=None):
        """
        `Author`: Bill Clark

        Shows the image if an image is given, otherwise defaults to the class's image.

        `image`: The image to show, defaults to the image contained in the class.
        """
        if not image: image = self.outimage
        image.show()

    def save(self, image=None, outfile=None):
        """
        `Author`: Bill Clark

        Saves an image to disk. The image can be specified, other wise the class's image is defaulted to.
        The outfile can also be optionally specified.

        `image`: Defaults to the class's image unless specified. The image to be saved.

        `outfile`: The location to save to. Defaults to the class's output path.
        """
        if not image: image = self.outimage
        if not outfile: outfile = self.outfile
        image.save(outfile)

    def printDiffSame(self, counter):
        """
        `Author`: Bill Clark

        Prints the different pixel percentage and the same pixel percentage.

        `counter`: The count of changed pixels in a merge operation. Obtained from checkandact.
        """
        print "Different Pixels:", counter, repr(round((counter/360000.)*100,2)) + '%', " Same Pixels:", \
            360000-counter, repr(round(((360000-counter)/360000.)*100,2)) + '%'+ '\n'


if __name__ == "__main__":
    debug = 0
    inputs = ['Input/IMG_0971.jpg', 'Input/IMG_0972.jpg']
    m = Merger('Output/ImF.png')

    m.processor = PixelProcess.ExtractPixelRemote()
    m.processor.setActorCommand(PixelProcess.RedHighlightCommand())
    m.processor.setCheckCommand(PixelProcess.ColorDiffCommand())

    m.merge(inputs[0])
    m.merge(inputs[1])
    print "Number of pixels recorded.", len(m.processor.pixels)

    post = m.processor.getGroupedPixels()

    print post[0], "W", post[0].width, "H", post[0].height
    print "RATIO", post[0].height / Image.open(inputs[0]).height


    # for group in post:  # Post the groups to the outimage.
    #     for p in group.pixels:
    #         imdata[p[0], p[1]] = m.processor.pixels[p]

    #Output the first group to it's own image.
    im = Image.new("RGBA", (post[0].width, post[0].height))
    imdata = im.load()

    for p in post[0].pixels:
        imdata[p[0]-post[0].x[0], p[1]-post[0].y[0]] = m.processor.pixels[p]

    im.show()
    im.save('Output/Only Pixels.png')

    m.processor.setActorCommand(PixelProcess.RedHighlightCommand())

    m.processor.checkcmd.diffnum = 50
    m.exportMerge('Output/DifferenceFile.png', 'Output/One Fused Provided.jpg')

    m.save()
