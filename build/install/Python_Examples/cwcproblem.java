import java.util.LinkedList;
import JSHOP2.*;

public class cwcproblem
{
	private static String[] defineConstants()
	{
		String[] problemConstants = new String[20];

		problemConstants[0] = "b6";
		problemConstants[1] = "b7";
		problemConstants[2] = "b8";
		problemConstants[3] = "b9";
		problemConstants[4] = "b10";
		problemConstants[5] = "b11";
		problemConstants[6] = "b12";
		problemConstants[7] = "b13";
		problemConstants[8] = "b14";
		problemConstants[9] = "b15";
		problemConstants[10] = "b16";
		problemConstants[11] = "b17";
		problemConstants[12] = "b18";
		problemConstants[13] = "b19";
		problemConstants[14] = "b5";
		problemConstants[15] = "b1";
		problemConstants[16] = "b2";
		problemConstants[17] = "b3";
		problemConstants[18] = "b4";
		problemConstants[19] = "b1000";

		return problemConstants;
	}

	private static void createState0(State s)	{
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(13), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(13), new TermList(new TermNumber(100.0), new TermList(new TermNumber(105.0), new TermList(new TermNumber(100.0), TermList.NIL))))));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(13), TermList.NIL)));
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(13), TermList.NIL)));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(14), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(14), new TermList(new TermNumber(100.0), new TermList(new TermNumber(106.0), new TermList(new TermNumber(100.0), TermList.NIL))))));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(14), TermList.NIL)));
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(14), TermList.NIL)));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(15), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(15), new TermList(new TermNumber(100.0), new TermList(new TermNumber(107.0), new TermList(new TermNumber(100.0), TermList.NIL))))));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(15), TermList.NIL)));
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(15), TermList.NIL)));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(16), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(16), new TermList(new TermNumber(100.0), new TermList(new TermNumber(108.0), new TermList(new TermNumber(100.0), TermList.NIL))))));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(16), TermList.NIL)));
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(16), TermList.NIL)));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(17), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(17), new TermList(new TermNumber(100.0), new TermList(new TermNumber(109.0), new TermList(new TermNumber(100.0), TermList.NIL))))));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(17), TermList.NIL)));
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(17), TermList.NIL)));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(18), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(18), new TermList(new TermNumber(100.0), new TermList(new TermNumber(110.0), new TermList(new TermNumber(100.0), TermList.NIL))))));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(18), TermList.NIL)));
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(18), TermList.NIL)));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(19), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(19), new TermList(new TermNumber(100.0), new TermList(new TermNumber(111.0), new TermList(new TermNumber(100.0), TermList.NIL))))));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(19), TermList.NIL)));
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(19), TermList.NIL)));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(20), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(20), new TermList(new TermNumber(100.0), new TermList(new TermNumber(112.0), new TermList(new TermNumber(100.0), TermList.NIL))))));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(20), TermList.NIL)));
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(20), TermList.NIL)));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(21), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(21), new TermList(new TermNumber(100.0), new TermList(new TermNumber(113.0), new TermList(new TermNumber(100.0), TermList.NIL))))));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(21), TermList.NIL)));
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(21), TermList.NIL)));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(22), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(22), new TermList(new TermNumber(100.0), new TermList(new TermNumber(114.0), new TermList(new TermNumber(100.0), TermList.NIL))))));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(22), TermList.NIL)));
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(22), TermList.NIL)));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(23), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(23), new TermList(new TermNumber(100.0), new TermList(new TermNumber(115.0), new TermList(new TermNumber(100.0), TermList.NIL))))));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(23), TermList.NIL)));
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(23), TermList.NIL)));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(24), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(24), new TermList(new TermNumber(100.0), new TermList(new TermNumber(116.0), new TermList(new TermNumber(100.0), TermList.NIL))))));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(24), TermList.NIL)));
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(24), TermList.NIL)));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(25), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(25), new TermList(new TermNumber(100.0), new TermList(new TermNumber(117.0), new TermList(new TermNumber(100.0), TermList.NIL))))));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(25), TermList.NIL)));
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(25), TermList.NIL)));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(26), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(26), new TermList(new TermNumber(100.0), new TermList(new TermNumber(118.0), new TermList(new TermNumber(100.0), TermList.NIL))))));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(26), TermList.NIL)));
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(26), TermList.NIL)));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(27), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(27), new TermList(new TermNumber(0.0), new TermList(new TermNumber(0.0), new TermList(new TermNumber(0.0), TermList.NIL))))));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(28), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(28), new TermList(new TermNumber(0.0), new TermList(new TermNumber(0.0), new TermList(new TermNumber(1.0), TermList.NIL))))));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(29), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(29), new TermList(new TermNumber(0.0), new TermList(new TermNumber(0.0), new TermList(new TermNumber(2.0), TermList.NIL))))));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(30), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(30), new TermList(new TermNumber(0.0), new TermList(new TermNumber(0.0), new TermList(new TermNumber(3.0), TermList.NIL))))));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(31), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(31), new TermList(new TermNumber(0.0), new TermList(new TermNumber(0.0), new TermList(new TermNumber(4.0), TermList.NIL))))));
		s.add(new Predicate(6, 0, new TermList(TermConstant.getConstant(32), TermList.NIL)));
		s.add(new Predicate(2, 0, new TermList(TermConstant.getConstant(32), new TermList(new TermNumber(1.0), new TermList(new TermNumber(1.0), new TermList(new TermNumber(0.0), TermList.NIL))))));
		s.add(new Predicate(4, 0, new TermList(TermConstant.getConstant(29), new TermList(TermConstant.getConstant(28), TermList.NIL))));
		s.add(new Predicate(4, 0, new TermList(TermConstant.getConstant(30), new TermList(TermConstant.getConstant(29), TermList.NIL))));
		s.add(new Predicate(4, 0, new TermList(TermConstant.getConstant(31), new TermList(TermConstant.getConstant(30), TermList.NIL))));
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(31), TermList.NIL)));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(27), TermList.NIL)));
		s.add(new Predicate(4, 0, new TermList(TermConstant.getConstant(28), new TermList(TermConstant.getConstant(27), TermList.NIL))));
		s.add(new Predicate(1, 0, new TermList(TermConstant.getConstant(32), TermList.NIL)));
		s.add(new Predicate(0, 0, new TermList(TermConstant.getConstant(32), TermList.NIL)));
	}

	public static LinkedList<Plan> getPlans()
	{
		LinkedList<Plan> returnedPlans = new LinkedList<Plan>();
		TermConstant.initialize(33);

		Domain d = new cwcdomain();

		d.setProblemConstants(defineConstants());

		State s = new State(13, d.getAxioms());

		JSHOP2.initialize(d, s);

		TaskList tl;
		SolverThread thread;

		createState0(s);

		tl = new TaskList(1, true);
		tl.subtasks[0] = new TaskList(new TaskAtom(new Predicate(6, 0, new TermList(new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(28), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(28), new TermList(new TermNumber(0.0), new TermList(new TermNumber(0.0), new TermList(new TermNumber(1.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(29), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(29), new TermList(new TermNumber(0.0), new TermList(new TermNumber(0.0), new TermList(new TermNumber(2.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(30), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(30), new TermList(new TermNumber(0.0), new TermList(new TermNumber(0.0), new TermList(new TermNumber(3.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(31), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(31), new TermList(new TermNumber(0.0), new TermList(new TermNumber(0.0), new TermList(new TermNumber(4.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(27), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(27), new TermList(new TermNumber(0.0), new TermList(new TermNumber(0.0), new TermList(new TermNumber(0.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(13), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(13), new TermList(new TermNumber(1.0), new TermList(new TermNumber(0.0), new TermList(new TermNumber(0.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(14), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(14), new TermList(new TermNumber(2.0), new TermList(new TermNumber(0.0), new TermList(new TermNumber(0.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(15), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(15), new TermList(new TermNumber(0.0), new TermList(new TermNumber(1.0), new TermList(new TermNumber(0.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(16), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(16), new TermList(new TermNumber(1.0), new TermList(new TermNumber(1.0), new TermList(new TermNumber(0.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(17), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(17), new TermList(new TermNumber(2.0), new TermList(new TermNumber(1.0), new TermList(new TermNumber(0.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(18), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(18), new TermList(new TermNumber(0.0), new TermList(new TermNumber(2.0), new TermList(new TermNumber(0.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(19), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(19), new TermList(new TermNumber(1.0), new TermList(new TermNumber(2.0), new TermList(new TermNumber(0.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(20), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(20), new TermList(new TermNumber(2.0), new TermList(new TermNumber(2.0), new TermList(new TermNumber(0.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(21), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(21), new TermList(new TermNumber(0.0), new TermList(new TermNumber(3.0), new TermList(new TermNumber(0.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(22), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(22), new TermList(new TermNumber(1.0), new TermList(new TermNumber(3.0), new TermList(new TermNumber(0.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(23), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(23), new TermList(new TermNumber(2.0), new TermList(new TermNumber(3.0), new TermList(new TermNumber(0.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(24), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(24), new TermList(new TermNumber(0.0), new TermList(new TermNumber(4.0), new TermList(new TermNumber(0.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(25), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(25), new TermList(new TermNumber(1.0), new TermList(new TermNumber(4.0), new TermList(new TermNumber(0.0), TermList.NIL))))), new TermList(new TermList(TermConstant.getConstant(6), new TermList(TermConstant.getConstant(26), TermList.NIL)), new TermList(new TermList(TermConstant.getConstant(2), new TermList(TermConstant.getConstant(26), new TermList(new TermNumber(2.0), new TermList(new TermNumber(4.0), new TermList(new TermNumber(0.0), TermList.NIL))))), TermList.NIL)))))))))))))))))))))))))))))))))))))), TermList.NIL)), false, false));

		thread = new SolverThread(tl, 1);
		thread.start();

		try {
			while (thread.isAlive())
				Thread.sleep(500);
		} catch (InterruptedException e) {
		}

		returnedPlans.addAll( thread.getPlans() );

		return returnedPlans;
	}

	public static LinkedList<Predicate> getFirstPlanOps() {
		return getPlans().getFirst().getOps();
	}
}