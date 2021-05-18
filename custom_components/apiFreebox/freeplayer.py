class Freeplayer:

    def __init__(self, access):
        self._access = access


    def get_freeplayer_list(self):
        '''
        Get freeplugs list
        '''
        return self._access.get('player/')
    #http://mafreebox.freebox.fr/api/v6/player


    def get_freeplayer(self, fp_id, version ="v8"):
        '''
        Get freeplug with the specific id
        '''
        return self._access.get('player/{0}/api/{1}/status/'.format(fp_id, version))
