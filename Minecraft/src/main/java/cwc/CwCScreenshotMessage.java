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
        this.type = CwCScreenshotEventType.values()[ByteBufUtils.readVarInt(buf, 5)];
        this.onUpdate = ByteBufUtils.readVarInt(buf, 5) > 0 ? true : false;
    }

    @Override
    public void toBytes(ByteBuf buf) {
        ByteBufUtils.writeVarInt(buf, type.ordinal(), 5);
        ByteBufUtils.writeVarInt(buf, this.onUpdate ? 1 : 0, 5);
    }

    public CwCScreenshotEventType getType() { return this.type; }
    public boolean onUpdate() { return this.onUpdate; }
}
