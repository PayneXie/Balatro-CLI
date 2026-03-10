from .enums import BlindType

class Blind:
    # 盲注信息表: (Base Reward, Score Multiplier)
    # GBA代码: SMALL -> 3, 1x; BIG -> 4, 1.5x; BOSS -> 5, 2x
    BLIND_INFO = {
        BlindType.SMALL: (3, 1.0),
        BlindType.BIG: (4, 1.5),
        BlindType.BOSS: (5, 2.0)
    }

    # 基础注额表 (对应 Ante 1-8)
    # GBA代码: 100, 300, 800, 2000, 5000, 11000, 20000, 35000, 50000
    # 注意：数组索引从0开始，Ante 1 对应索引 0
    ANTE_BASE_SCORES = [300, 800, 2000, 5000, 11000, 20000, 35000, 50000]

    def __init__(self, type: BlindType, ante: int):
        self.type = type
        self.ante = ante
        self.reward = self.BLIND_INFO[type][0]
        self.score_requirement = self._calculate_requirement()

    def _calculate_requirement(self) -> int:
        if self.ante < 1 or self.ante > len(self.ANTE_BASE_SCORES):
            # 超出范围，简单指数增长作为后备
            base = 50000 * (1.5 ** (self.ante - 8))
            return int(base)
        
        base_score = self.ANTE_BASE_SCORES[self.ante - 1]
        multiplier = self.BLIND_INFO[self.type][1]
        return int(base_score * multiplier)

    def __str__(self):
        return f"{self.type.name} Blind (Ante {self.ante}): Target {self.score_requirement}, Reward ${self.reward}"
