import enum
import struct
import functools
from typing import TYPE_CHECKING

@enum.unique
class ClientPackets(enum.IntEnum):
    CHANGE_ACTION = 0
    SEND_PUBLIC_MESSAGE = 1
    LOGOUT = 2
    REQUEST_STATUS_UPDATE = 3
    PING = 4
    START_SPECTATING = 16
    STOP_SPECTATING = 17
    SPECTATE_FRAMES = 18
    ERROR_REPORT = 20
    CANT_SPECTATE = 21
    SEND_PRIVATE_MESSAGE = 25
    PART_LOBBY = 29
    JOIN_LOBBY = 30
    CREATE_MATCH = 31
    JOIN_MATCH = 32
    PART_MATCH = 33
    MATCH_CHANGE_SLOT = 38
    MATCH_READY = 39
    MATCH_LOCK = 40
    MATCH_CHANGE_SETTINGS = 41
    MATCH_START = 44    
    MATCH_SCORE_UPDATE = 47
    MATCH_COMPLETE = 49
    MATCH_CHANGE_MODS = 51
    MATCH_LOAD_COMPLETE = 52
    MATCH_NO_BEATMAP = 54
    MATCH_NOT_READY = 55
    MATCH_FAILED = 56
    MATCH_HAS_BEATMAP = 59
    MATCH_SKIP_REQUEST = 60
    CHANNEL_JOIN = 63
    BEATMAP_INFO_REQUEST = 68
    MATCH_TRANSFER_HOST = 70
    FRIEND_ADD = 73
    FRIEND_REMOVE = 74
    MATCH_CHANGE_TEAM = 77
    CHANNEL_PART = 78
    RECEIVE_UPDATES = 79
    SET_AWAY_MESSAGE = 82
    IRC_ONLY = 84
    USER_STATS_REQUEST = 85
    MATCH_INVITE = 87
    MATCH_CHANGE_PASSWORD = 90
    TOURNAMENT_MATCH_INFO_REQUEST = 93
    USER_PRESENCE_REQUEST = 97
    USER_PRESENCE_REQUEST_ALL = 98
    TOGGLE_BLOCK_NON_FRIEND_DMS = 99
    TOURNAMENT_JOIN_MATCH_CHANNEL = 108
    TOURNAMENT_LEAVE_MATCH_CHANNEL = 109

@enum.unique
class ServerPackets(enum.IntEnum):
    USER_ID = 5
    SEND_MESSAGE = 7
    PONG = 8
    HANDLE_IRC_CHANGE_USERNAME = 9
    HANDLE_IRC_QUIT = 10
    USER_STATS = 11
    USER_LOGOUT = 12
    SPECTATOR_JOINED = 13
    SPECTATOR_LEFT = 14
    SPECTATE_FRAMES = 15
    VERSION_UPDATE = 19
    SPECTATOR_CANT_SPECTATE = 22
    GET_ATTENTION = 23
    NOTIFICATION = 24
    UPDATE_MATCH = 26
    NEW_MATCH = 27
    DISPOSE_MATCH = 28
    TOGGLE_BLOCK_NON_FRIEND_DMS = 34
    MATCH_JOIN_SUCCESS = 36
    MATCH_JOIN_FAIL = 37
    FELLOW_SPECTATOR_JOINED = 42
    FELLOW_SPECTATOR_LEFT = 43
    ALL_PLAYERS_LOADED = 45
    MATCH_START = 46
    MATCH_SCORE_UPDATE = 48
    MATCH_TRANSFER_HOST = 50
    MATCH_ALL_PLAYERS_LOADED = 53
    MATCH_PLAYER_FAILED = 57
    MATCH_COMPLETE = 58
    MATCH_SKIP = 61
    UNAUTHORIZED = 62 # unused
    CHANNEL_JOIN_SUCCESS = 64
    CHANNEL_INFO = 65
    CHANNEL_KICK = 66
    CHANNEL_AUTO_JOIN = 67
    BEATMAP_INFO_REPLY = 69
    PRIVILEGES = 71
    FRIENDS_LIST = 72
    PROTOCOL_VERSION = 75
    MAIN_MENU_ICON = 76
    MONITOR = 80 # unused
    MATCH_PLAYER_SKIPPED = 81
    USER_PRESENCE = 83
    RESTART = 86
    MATCH_INVITE = 88
    CHANNEL_INFO_END = 89
    MATCH_CHANGE_PASSWORD = 91
    SILENCE_END = 92
    USER_SILENCED = 94
    USER_PRESENCE_SINGLE = 95
    USER_PRESENCE_BUNDLE = 96
    USER_DM_BLOCKED = 100
    TARGET_IS_SILENCED = 101
    VERSION_UPDATE_FORCED = 102
    SWITCH_SERVER = 103
    ACCOUNT_RESTRICTED = 104
    RTX = 105 # unused
    MATCH_ABORT = 106
    SWITCH_TOURNAMENT_SERVER = 107

def write_uleb128(num: int) -> bytes:
    if num == 0:
        return bytearray(b'\x00')

    ret = bytearray()
    length = 0

    while num > 0:
        ret.append(num & 0b01111111)
        num >>= 7
        if num != 0:
            ret[length] |= 0b10000000
        length += 1

    return bytes(ret)

def write_string(string: str) -> bytes:
    s = string.encode()
    return b'\x0b' + write_uleb128(len(s)) + s

def write_int(i: int) -> bytes:
    return struct.pack('<i', i)

def write_unsigned_int(i: int) -> bytes:
    return struct.pack('<I', i)

def write_float(f: float) -> bytes:
    return struct.pack('<f', f)

def write_byte(b: int) -> bytes:
    return struct.pack('<b', b)

def write_unsigned_byte(b: int) -> bytes:
    return struct.pack('<B', b)

def write_short(s: int) -> bytes:
    return struct.pack('<h', s)

def write_long_long(l: int) -> bytes:
    return struct.pack('<q', l)

def write_list32(l: tuple[int]) -> bytes:
    ret = bytearray(write_short(len(l)))

    for item in l:
        ret += write_int(item)

    return bytes(ret)

def write(packetid: int, *args) -> bytes:
    p = bytearray(struct.pack('<Hx', packetid))

    for ctx, _type in args:
        if _type == 'str':
            p += write_string(ctx)
        elif _type == 'int':
            p += write_int(ctx)
        elif _type == 'unint':
            p += write_unsigned_int(ctx)
        elif _type == 'short':
            p += write_short(ctx)
        elif _type == 'float':
            p += write_float(ctx)
        elif _type == 'long':
            p += write_long_long(ctx)
        elif _type == 'byte':
            p += write_byte(ctx)
        elif _type == 'unbyte':
            p += write_unsigned_byte(ctx)
        elif _type == 'list_32':
            p += write_list32(ctx)
        else:
            p += struct.pack(f'<{_type}', ctx)

    p[3:3] = struct.pack('<I', len(p) - 3)
    return bytes(p)

@functools.cache
def userID(i: int) -> bytes:
    return write(
        ServerPackets.USER_ID,
        (i, f"{'unint' if i > 0 else 'int'}")
    )

@functools.cache
def notification(msg: str) -> bytes:
    return write(
        ServerPackets.NOTIFICATION,
        (msg, 'str')
    )

@functools.cache
def protocolVersion(i: int = 19):
    return write(
        ServerPackets.PROTOCOL_VERSION, (i, 'int')
    )

@functools.cache
def banchoPrivs(privs: int) -> bytes:
    return write(
        ServerPackets.PRIVILEGES, (privs, 'int')
    )

def userPresence(
    user_id: int,
    user_name: str,
    utc_offset: int,
    country_code: int,
    bancho_privs: int,
    game_mode: int,
    location: tuple[int, int],
    rank: int
) -> bytes:
    return write(
        ServerPackets.USER_PRESENCE,
        (user_id, 'int'), (user_name, 'str'),
        (utc_offset + 24, 'unbyte'), (country_code, 'unbyte'),
        (bancho_privs | game_mode << 5, 'unbyte'), (location[0], 'float'),
        (location[1], 'float'), (rank, 'int')
    )

def userStats(
    user_id: int,
    action: int,
    info_text: str,
    map_md5: str,
    mods: int,
    game_mode: int,
    map_id: int,
    ranked_score: int,
    acc: float,
    playcount: int,
    total_score: int,
    rank: int,
    pp: int
) -> bytes:
    return write(
        ServerPackets.USER_STATS,
        (user_id, 'int'), (action, 'byte'),
        (info_text, 'str'), (map_md5, 'str'),
        (mods, 'int'), (game_mode, 'unbyte'),
        (map_id, 'int'), (ranked_score, 'long'),
        (acc / 100.0, 'float'), (playcount, 'int'),
        (total_score, 'long'), (rank, 'int'),
        (pp, 'short')
    )

@functools.cache
def menuIcon(menu_icon: tuple[str, str]) -> bytes:
    return write(
        ServerPackets.MAIN_MENU_ICON,
        ('|'.join(menu_icon), 'str')
    )

def friendsList(*friends: int) -> bytes:
    return write(
        ServerPackets.FRIENDS_LIST,
        (friends, 'list_32')
    )

@functools.cache
def channelInfoEnd() -> bytes:
    return write(ServerPackets.CHANNEL_INFO_END)

def channelJoin(channel_name: str) -> bytes:
    return write(
        ServerPackets.CHANNEL_JOIN_SUCCESS, (channel_name, 'str')
    )

def channelInfo(
    channel_name: str,
    channel_description: str,
    channel_player_count: int
) -> bytes:
    return write(
        ServerPackets.CHANNEL_INFO,
        (channel_name, 'str'), (channel_description, 'str'), (channel_player_count, 'short')
    )

def friendslist(*friends) -> bytes:
    return write(
        ServerPackets.FRIENDS_LIST,
        (friends, 'list_32')
    )

@functools.cache
def systemRestart(ms: int = 0) -> bytes:
    return write(
        ServerPackets.RESTART, (ms, 'int')
    )

@functools.cache
def logout(uid: int) -> bytes:
    return write(
        ServerPackets.USER_LOGOUT,
        (uid, 'int'), (0, 'unbyte')
    )

@functools.cache
def sendMsg(client: str, msg: str, target: str, userid: int):
    return write(
        ServerPackets.SEND_MESSAGE,
        (client, 'str'), (msg, 'str'),
        (target, 'str'), (userid, 'int')
    )

@functools.cache
def userSilenced(userid: int) -> bytes:
    return write(
        ServerPackets.USER_SILENCED,
        (userid, 'int')
    )