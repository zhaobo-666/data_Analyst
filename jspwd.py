from pyDes import des, PAD_PKCS5, ECB


class Dess(object):
    def __init__(self):
        self.key = 'd0cddaaa'
        self.des_obj = des(self.key, ECB, self.key, padmode=PAD_PKCS5)

    def en_des(self, text):
        secret_bytes = self.des_obj.encrypt(text)
        return secret_bytes

    def de_des(self, text):
        de_des = self.des_obj.decrypt(text)
        return de_des


if __name__ == '__main__':
    desc = Dess()
    test = desc.en_des('xsacac455')
    print(test)
    test = desc.de_des(test)
    print(test)
