package cwc;

import com.microsoft.Malmo.Client.MalmoModClient;
import com.microsoft.Malmo.MalmoMod;
import net.minecraft.client.Minecraft;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraft.util.ScreenShotHelper;
import net.minecraft.world.WorldServer;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;
import net.minecraftforge.fml.common.network.simpleimpl.IMessageHandler;
import net.minecraftforge.fml.common.network.simpleimpl.MessageContext;
import net.minecraftforge.fml.relauncher.Side;

import java.io.File;
import java.util.Date;

public class CwCMessageHandler implements IMessageHandler<CwCStateMessage, IMessage> {
    public IMessage onMessage(final CwCStateMessage message, MessageContext ctx) {
        if (ctx.side == Side.SERVER) {
            final EntityPlayerMP sender = ctx.getServerHandler().playerEntity;
            if (ctx.getServerHandler().playerEntity == null) return null;

            final WorldServer pws = sender.getServerWorld();
            pws.addScheduledTask(new Runnable() {
                public void run() { processMessageOnServer(message, sender); }
            });

            return null;
        }

        else {
            final Minecraft minecraft = Minecraft.getMinecraft();
            minecraft.addScheduledTask(new Runnable() {
                public void run() { processMessageOnClient(message, minecraft); }
            });

            return null;
        }
    }

    void processMessageOnServer(CwCStateMessage message, EntityPlayerMP sender) {
        for (EntityPlayerMP player : sender.mcServer.getPlayerList().getPlayers())
            CwCMod.network.sendTo(message, player);
    }

    void processMessageOnClient(CwCStateMessage message, Minecraft mc) {
        CwCMod.state = CwCState.valueOf(message.getState());
        EntityPlayer player = mc.player;

        if (CwCMod.state == CwCState.INSPECTING) {
            CwCEventHandler.reset = true;
            if (player.getName().equals(MalmoMod.BUILDER) && mc.mouseHelper instanceof MalmoModClient.MouseHook)
                ((MalmoModClient.MouseHook) mc.mouseHelper).isOverriding = true;
        }

        else if (CwCMod.state == CwCState.BUILDING && player.getName().equals(MalmoMod.BUILDER) && mc.mouseHelper instanceof MalmoModClient.MouseHook)
            ((MalmoModClient.MouseHook) mc.mouseHelper).isOverriding = false;

        ScreenShotHelper.saveScreenshot(CwCMod.loggingDir, (getTimestampedPNGFileForDirectory(CwCMod.screenshotDir)+"-"+player.getName())
                .replace(CwCMod.screenshotDir.getAbsolutePath(),""), mc.displayWidth, mc.displayHeight, mc.getFramebuffer());
    }

    /**
     * Creates a unique PNG file in the given directory named by a timestamp.  Handles cases where the timestamp alone
     * is not enough to create a uniquely named file, though it still might suffer from an unlikely race condition where
     * the filename was unique when this method was called, but another process or thread created a file at the same
     * path immediately after this method returned.
     */
    private static File getTimestampedPNGFileForDirectory(File gameDirectory) {
        String s = CwCMod.DATE_FORMAT.format(new Date()).toString();
        int i = 1;

        while (true) {
            File file1 = new File(gameDirectory, s + (i == 1 ? "" : "_" + i) + ".png");
            if (!file1.exists()) return file1;
            ++i;
        }
    }
}
