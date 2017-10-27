package cwc;

import io.netty.buffer.ByteBuf;
import net.minecraftforge.fml.common.network.ByteBufUtils;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;

public class CwCScreenshotMessage implements IMessage {
    private CwCScreenshotEventType type;
    private boolean onUpdate;

    public CwCScreenshotMessage() {}
    public CwCScreenshotMessage(CwCScreenshotEventType type, boolean onUpdate) {
        this.type = type;
        this.onUpdate = onUpdate;
    }

    @Override
    public void fromBytes(ByteBuf buf) {
//        this.type = ByteBufUtils.readUTF8String(buf);
//        this.onUpdate = ByteBufUtils.readUTF8String(buf);
    }

    @Override
    public void toBytes(ByteBuf buf) {
//        ByteBufUtils.writeUTF8String(buf, type);
//        ByteBufUtils.writeUTF8String(buf, onUpdate);
    }

    public CwCScreenshotEventType getType()  { return this.type; }
    public boolean onUpdate() { return this.onUpdate; }
}
