class AnimationManager:
    def __init__(self):
        self.animations = []

# TODO: animation layer? need animations to run simultaneously
# when applicable
    def render(self):
        drop_list = []
        for a in self.animations:
            a.increment()
            if a.running:
                img_idx = a.img_idx
                blt.print(a.xs[img_idx], a.ys[img_idx], a.images[img_idx])
            else:
                drop_list.append(a)
        self._update(drop_list)

    def _update(self, drop_list):
        if drop_list:
            for a in drop_list:
                self.animations.remove(a)


class Animation:
    def __init__(self, images, durations, xs, ys):
        self.images = images
        self.num_imgs = len(images)
        self.durations = durations
        self.xs = xs
        self.ys = ys
        self.frame = 0
        self.img_idx = 0
        self.running = True

    def increment(self):
        if self.frame >= durations[self.index]:
            self.index += 1
            if self.index > self.num_imgs:
                self.running = False
            self.frame = 0
        else:
            self.frame += 1
