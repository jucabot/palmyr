from common.context import UserContext
from common.command import Command
from django.contrib.auth.decorators import login_required
import traceback

@login_required
def api(request):
    
    cmd_op = request.GET['cmd']
    ctx = UserContext(request)
    cmd = Command(ctx)
    try:
        
        if cmd_op == 'clear-cache':
            return cmd.clear_cache()
        else:
            return cmd.error('Undefined api command %s' % cmd_op)

    except Exception, e:
        print traceback.format_exc()
        return cmd.error(str(e))

 