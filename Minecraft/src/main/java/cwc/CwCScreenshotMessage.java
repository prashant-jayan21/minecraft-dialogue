package cwc;

import io.netty.buffer.ByteBuf;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;

public class CwCScreenshotMessage implements IMessage {
    private CwCScreenshotEventType type;

    public CwCScreenshotMessage() {}
    public CwCScreenshotMessage(CwCScreenshotEventType type) {
        this.type = type;
    }

    @Override
    public void fromBytes(ByteBuf buf) { this.type = CwCScreenshotEventType.values()[buf.readInt()]; }

    @Override
    public void toBytes(ByteBuf buf) { buf.writeInt(this.type.ordinal()); }

    public CwCScreenshotEventType getType() { return this.type; }
}
