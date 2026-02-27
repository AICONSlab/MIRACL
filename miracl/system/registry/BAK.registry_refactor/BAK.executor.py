from miracl.system.registry.registry_refactor.datamodels import CommandPlan


class MiraclExecutor:
    @staticmethod
    def execute(execution_plans: CommandPlan):
        for plan in execution_plans:
            print(f"Module:                 {plan.module_name}")
            plan.runner(plan.tokens, plan.execute)
