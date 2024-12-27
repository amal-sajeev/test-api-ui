from wizard import *
import wizard

testwizard = wizard.LearningPlatformSDK("http://localhost:8100")

print(testwizard.get_all_drafts("testertest"))