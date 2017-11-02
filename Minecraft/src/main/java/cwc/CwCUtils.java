package cwc;

import net.minecraft.client.Minecraft;
import net.minecraft.util.ScreenShotHelper;

import java.io.File;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * General-purpose utility class.
 * @author nrynchn2
 */
public class CwCUtils {
    public static String[] statusOverlay = {"Architect is inspecting...", "Architect is thinking...", "Builder is building..."};  // status overlay strings (for indicating current game state)

    public static boolean useTimestamps = false;    // whether or not to include timestamps as part of screenshot names
    private static final DateFormat DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd_HH.mm.ss");  // timestamp date format
    private static int index = 1;        // if not using timestamps, index prefix of screenshots taken

    private static File loggingDir;      // directory of observation logs
    private static File screenshotDir;   // directory of screenshots (within logging directory)
    static {
        loggingDir = new File(System.getProperty("user.dir"));
        screenshotDir = new File(loggingDir, "screenshots");
        if (!screenshotDir.exists()) screenshotDir.mkdir();
    }

    /**
     * Creates a unique PNG file in the given directory named by a timestamp.  Handles cases where the timestamp alone
     * is not enough to create a uniquely named file, though it still might suffer from an unlikely race condition where
     * the filename was unique when this method was called, but another process or thread created a file at the same
     * path immediately after this method returned.
     *
     * Taken from Minecraft's {@link ScreenShotHelper}.
     *
     * @param gameDirectory Path to game directory
     */
    public static String getTimestampedFileForDirectory(File gameDirectory) {
        String s = DATE_FORMAT.format(new Date()).toString();
        int i = 1;

        while (true) {
            File file1 = new File(gameDirectory, s + (i == 1 ? "" : "_" + i));
            if (!file1.exists()) return file1.getAbsolutePath().replace(gameDirectory.getAbsolutePath(),"");
            ++i;
        }
    }

    /**
     * Takes a screenshot with the appropriate filename.
     * @param mc Minecraft client
     * @param timestamp Whether or not to use timestamp in the screenshot filename
     * @param type Type of event that triggered this screenshot action
     */
    public static void takeScreenshot(Minecraft mc, boolean timestamp, CwCScreenshotEventType type) {
        //TODO: append mission name, experiment number, architect/builder IDs somewhere to this path!
        String prefix = timestamp ? CwCUtils.getTimestampedFileForDirectory(screenshotDir) : index+"";  // prefix with either timestamp or screenshot index
        String suffix = CwCMod.state.name().toLowerCase()+"-"+type.name().toLowerCase();  // suffix with type of triggering event

        // take the screenshot
        ScreenShotHelper.saveScreenshot(CwCUtils.loggingDir, prefix+"-"+mc.player.getName()+"-"+suffix+".png", mc.displayWidth, mc.displayHeight, mc.getFramebuffer());

        // save screenshot filename to list
        CwCMod.screenshots.add(CwCUtils.screenshotDir+"/"+prefix+"-"+mc.player.getName()+"-"+suffix+".png");
        System.out.println("Screenshot: "+CwCMod.screenshots.get(CwCMod.screenshots.size()-1));
        index++;

        if (type == CwCScreenshotEventType.PICKUP) CwCEventHandler.disablePickup = false;
        if (type == CwCScreenshotEventType.PUTDOWN) CwCEventHandler.disablePutdown = false;
    }
}
