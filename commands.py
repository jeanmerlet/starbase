from bearlibterminal import terminal as blt


MOVE_CMDS = {
    blt.TK_KP_1: (-1, 1),
    blt.TK_KP_2: (0, 1),
    blt.TK_KP_3: (1, 1),
    blt.TK_KP_4: (-1, 0),
    blt.TK_KP_6: (1, 0),
    blt.TK_KP_7: (-1, -1),
    blt.TK_KP_8: (0, -1),
    blt.TK_KP_9: (1, -1)
}

WAIT_CMDS = {
    blt.TK_KP_5,
    blt.TK_PERIOD
}

MAIN_CMDS = {
    blt.TK_D,
    blt.TK_E,
    blt.TK_F,
    blt.TK_G,
    blt.TK_I,
    blt.TK_U,
    blt.TK_T,
    blt.TK_X,
    blt.TK_GRAVE
}

QUIT_CMD = {
    blt.TK_Q
}

CANCEL_CMD = {
    blt.TK_ESCAPE
}

MENU_CMDS = {
    blt.TK_A,
    blt.TK_B,
    blt.TK_C,
    blt.TK_D,
    blt.TK_E,
    blt.TK_F,
    blt.TK_G,
    blt.TK_H,
    blt.TK_I,
    blt.TK_J,
    blt.TK_K,
    blt.TK_L,
    blt.TK_M,
    blt.TK_N,
    blt.TK_O,
    blt.TK_P,
    blt.TK_Q,
    blt.TK_R,
    blt.TK_S,
    blt.TK_T,
    blt.TK_U,
    blt.TK_V,
    blt.TK_W,
    blt.TK_X,
    blt.TK_Y,
    blt.TK_Z,
}

TARGET_CMDS = {
    blt.TK_TAB,
    blt.TK_F,
    blt.TK_ENTER,
    blt.TK_KP_ENTER
}
