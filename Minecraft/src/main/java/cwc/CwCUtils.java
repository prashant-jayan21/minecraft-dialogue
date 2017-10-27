package cwc;

import net.minecraft.client.Minecraft;
import net.minecraft.util.ScreenShotHelper;

import java.io.File;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;

public class CwCUtils {
    public static String[] statusOverlay = {"Architect is inspecting...", "Architect is thinking...", "Builder is building..."};
    public static boolean useTimestamps = false;
    public static int index = 1;
    public static final DateFormat DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd_HH.mm.ss");
    public static File loggingDir;
    public static File screenshotDir;
    static {
        loggingDir = new File("/Users/Anjali/Documents/UIUC/research/CwC/BlocksWorld/Minecraft/cwc-minecraft/");
        if (!loggingDir.exists()) loggingDir.mkdir();
        screenshotDir = new File(loggingDir, "screenshots");
        if (!screenshotDir.exists()) screenshotDir.mkdir();
    }

    /**
     * Creates a unique PNG file in the given directory named by a timestamp.  Handles cases where the timestamp alone
     * is not enough to create a uniquely named file, though it still might suffer from an unlikely race condition where
     * the filename was unique when this method was called, but another process or thread created a file at the same
     * path immediately after this method returned.
     */
    public static File getTimestampedFileForDirectory(File gameDirectory) {
        String s = DATE_FORMAT.format(new Date()).toString();
        int i = 1;

        while (true) {
            File file1 = new File(gameDirectory, s + (i == 1 ? "" : "_" + i));
            if (!file1.exists()) return file1;
            ++i;
        }
    }

    public static void takeScreenshot(Minecraft mc, boolean timestamp, CwCScreenshotEventType type, boolean onUpdate) {
        //TODO: append mission name, experiment number, architect/builder IDs somewhere to this path!
        String prefix = timestamp ? CwCUtils.getTimestampedFileForDirectory(screenshotDir)+"" : screenshotDir.getAbsolutePath()+index;
        String suffix = type.name().toLowerCase()+(type == CwCScreenshotEventType.CHAT ? "" : onUpdate ? "-before" : "-after");

        ScreenShotHelper.saveScreenshot(CwCUtils.loggingDir, (prefix+"-"+mc.player.getName()+"-"+suffix)
                .replace(screenshotDir.getAbsolutePath(),"")+".png", mc.displayWidth, mc.displayHeight, mc.getFramebuffer());

        CwCMod.screenshots.add(CwCUtils.loggingDir+(prefix+"-"+mc.player.getName()+"-"+suffix)
                .replace(screenshotDir.getAbsolutePath(),"")+".png");

        System.out.println("Screenshot: "+CwCUtils.loggingDir+"/"+(prefix+"-"+mc.player.getName()+"-"+suffix)
                .replace(screenshotDir.getAbsolutePath(),"")+".png");
        index++;
    }
}
