package cwc;

import io.netty.buffer.ByteBuf;

public enum CwCScreenshotEventType {
    CHAT,
    PICKUP,
    PUTDOWN;

    public void toBytes(ByteBuf buf) {  }
}
