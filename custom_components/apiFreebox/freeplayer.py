class Freeplayer:

    def __init__(self, access):
        self._access = access


    def get_freeplayer_list(self):
        '''
        Get freeplugs list
        '''
        return self._access.get('player/')
    #http://mafreebox.freebox.fr/api/v6/player


    def get_freeplayer(self, fp_id, version ="v12"):
        '''
        Get freeplug with the specific id
        '''
        return self._access.get('player/{0}/api/{1}/status/'.format(fp_id, version))

    def get_freeplayer_volume(self, fp_id, version ="v12"):
        #Get freebox volume
        return self._access.get('player/{0}/api/{1}/control/volume/'.format(fp_id, version))

    def get_freeplayer_ip(self, monPlayer, version = "v12"):
        #Get freebox player IP
        devices = self._access.get('lan/browser/pub')
        i=0
        for device in devices:
            i = i+1
            if (device["l2ident"]["id"].upper()==monPlayer["mac"].upper()):
                interfaces = device["l3connectivities"]
                for interface in interfaces :
                    if (interface["active"] and interface["af"]=="ipv4"):
                        return interface["addr"]
        return ""
