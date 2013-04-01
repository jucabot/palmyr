from django.contrib.auth.decorators import login_required
from web.context import UserContext
from command import FeatureTableCommand,error
import traceback
from web.api.command import GeneralCommand

def api_general(request):
    
    cmd = request.GET['cmd']
    ctx = UserContext(request)
    gcmd = GeneralCommand(ctx)
    try:
        if cmd == 'get-content':
            return gcmd.get_content()
        elif cmd == 'create-analysis':
            if not request.user.is_authenticated():
                return login_required()
            else:
                return gcmd.create_analysis()
        else:
                return error('Undefined api command %s' % cmd)

    except Exception, e:
        print traceback.format_exc()
        return error(str(e))
    
@login_required
def api_analysis(request):
    
    ftname = request.GET['ftable']
    cmd = request.GET['cmd']
    
    ctx = UserContext(request)
    try:
        if ctx.feature_table_exist(ftname):
            ftable = ctx.get_feature_table(ftname)
            ftcmd = FeatureTableCommand(ctx,ftname,ftable)
            
            if cmd == 'set-target':
                return ftcmd.set_target()
            elif cmd == 'reset-target':
                return ftcmd.reset_target()
            elif cmd == 'save':
                return ftcmd.save()
            elif cmd == 'set-class':
                return ftcmd.set_class()
            elif cmd == 'get-distribution-function':
                return ftcmd.get_distribution_function()
            elif cmd == 'use-feature':
                return ftcmd.use_feature()
            elif cmd == 'toggle-feature':
                return ftcmd.toggle_feature()
            elif cmd == 'build-model':
                return ftcmd.build_model()
            elif cmd == 'save-model':
                return ftcmd.save_model()
            elif cmd == 'add-feature':
                return ftcmd.add_feature()
            elif cmd == 'get-feature':
                return ftcmd.get_feature()
            elif cmd == 'edit-feature':
                return ftcmd.edit_feature()
            elif cmd == 'remove-feature':
                return ftcmd.remove_feature()
            elif cmd == 'select-best-features':
                return ftcmd.select_best_features()
            elif cmd == 'get-model-info':
                return ftcmd.get_model_info()
            elif cmd == 'get-current-model-info':
                return ftcmd.get_current_model_info()
            elif cmd == 'apply-prediction':
                return ftcmd.apply_prediction()
            elif cmd == 'nl-query':
                return ftcmd.nl_query()
            elif cmd == 'add-filter':
                return ftcmd.add_filter()
            elif cmd == 'select-filter':
                return ftcmd.select_filter()
            elif cmd == 'clear-filter':
                return ftcmd.clear_filter()
            else:
                return error('Undefined api command %s' % cmd)
        else:
            return error('No feature feature table %s' % ftname)
    except Exception, e:
        print traceback.format_exc()
        return error(str(e))