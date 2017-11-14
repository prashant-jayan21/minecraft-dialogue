package cwc;

import io.netty.buffer.ByteBuf;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;

/**
 * Custom message used for quitting out of missions.
 * @author nrynchn2
 */
public class CwCQuitMessage implements IMessage {
    private boolean quit;

    public CwCQuitMessage() {}
    public CwCQuitMessage(boolean quit) { this.quit = quit; }

    @Override
    public void fromBytes(ByteBuf buf) { this.quit = buf.readBoolean(); }

    @Override
    public void toBytes(ByteBuf buf) { buf.writeBoolean(this.quit); }

    public boolean quit() { return this.quit; }
}
