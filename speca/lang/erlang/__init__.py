GEN_SERVER_TEMPLATE = \
"""%%%-----------------------------------------------------------------------------
%%% File          : {{module_name}}.erl
%%% Author        : {{author}} <{{author_email}}>
%%% Description   : {{description}}
%%%
%%% Created       : {{date}}
%%%-----------------------------------------------------------------------------
-module({{module_name}}).

-behaviour(gen_server).

%%------------------------------------------------------------------------------
%% Exports
%%------------------------------------------------------------------------------
-export([start_link/0{{export_functions}}]).

%%------------------------------------------------------------------------------
%% gen_server callbacks export
%%------------------------------------------------------------------------------
-export([init/1, handle_call/3, handle_cast/2, handle_info/2,
	 terminate/2, code_change/3, shutdown/0]).


-define(SERVER, ?MODULE).
-record(state, {}).

%%------------------------------------------------------------------------------
%% Function: shutdown()
%% Description: shutdowns gen_server.
%%------------------------------------------------------------------------------

shutdown() ->
  gen_server:cast({global, ?SERVER}, stop).

{{proxy_functions}}

%%==============================================================================
%% API
%%==============================================================================
%%------------------------------------------------------------------------------
%% Function: start_link() -> {ok,Pid} | ignore | {error,Error}
%% Description: Starts the server
%%------------------------------------------------------------------------------
start_link() ->
    gen_server:start_link({{{start_mode}}, ?SERVER}, ?MODULE, [], []).

%%==============================================================================
%% gen_server callbacks
%%==============================================================================

%%------------------------------------------------------------------------------
%% Function: init(Args) -> {ok, State} |
%%                         {ok, State, Timeout} |
%%                         ignore               |
%%                         {stop, Reason}
%% Description: Initiates the server
%%------------------------------------------------------------------------------
init([]) ->
    process_flag(trap_exit, true),
    io:format("~p (~p) starting...~n", [?MODULE, self()]),
    {ok, #state{}}.

%%------------------------------------------------------------------------------
%% Function: %% handle_call(Request, From, State) -> {reply, Reply, State} |
%%                                      {reply, Reply, State, Timeout} |
%%                                      {noreply, State} |
%%                                      {noreply, State, Timeout} |
%%                                      {stop, Reason, Reply, State} |
%%                                      {stop, Reason, State}
%% Description: Handling call messages
%%------------------------------------------------------------------------------
{{handle_call_functions}}

handle_call(_Request, _From, State) ->
    Reply = ok,
    {reply, Reply, State}.

%%------------------------------------------------------------------------------
%% Function: handle_cast(Msg, State) -> {noreply, State} |
%%                                      {noreply, State, Timeout} |
%%                                      {stop, Reason, State}
%% Description: Handling cast messages
%%------------------------------------------------------------------------------
handle_cast(stop, State) ->
  {stop, normal, State};

handle_cast(_Msg, State) ->
    {noreply, State}.

%%------------------------------------------------------------------------------
%% Function: handle_info(Info, State) -> {noreply, State} |
%%                                       {noreply, State, Timeout} |
%%                                       {stop, Reason, State}
%% Description: Handling all non call/cast messages
%%------------------------------------------------------------------------------
handle_info(_Info, State) ->
    {noreply, State}.

%%------------------------------------------------------------------------------
%% Function: terminate(Reason, State) -> void()
%% Description: This function is called by a gen_server when it is about to
%% terminate. It should be the opposite of Module:init/1 and do any necessary
%% cleaning up. When it returns, the gen_server terminates with Reason.
%% The return value is ignored.
%%------------------------------------------------------------------------------
terminate(_Reason, _State) ->
    ok.

%%------------------------------------------------------------------------------
%% Func: code_change(OldVsn, State, Extra) -> {ok, NewState}
%% Description: Convert process state when code is changed
%%------------------------------------------------------------------------------
code_change(_OldVsn, State, _Extra) ->
    {ok, State}.

%%------------------------------------------------------------------------------
%%% Internal functions
%%------------------------------------------------------------------------------

"""

FSM_TEMPLATE = \
"""%%%-----------------------------------------------------------------------------
%%% File          : {{module_name}}.erl
%%% Author        : {{author}} <{{author_email}}>
%%% Description   : {{description}}
%%%
%%% Created       : {{date}}
%%%-----------------------------------------------------------------------------
-module({{module_name}}).

-behaviour(gen_fsm).

%% API
-export([start_link/0]).

%% gen_fsm callbacks
-export([init/1, state_name/2, state_name/3, handle_event/3,
	 handle_sync_event/4, handle_info/3, terminate/3, code_change/4]).

-record(state, {}).
-define(SERVER, ?MODULE).

%%==============================================================================
%% API
%%==============================================================================
%%------------------------------------------------------------------------------
%% Function: start_link() -> ok,Pid} | ignore | {error,Error}
%% Description:Creates a gen_fsm process which calls Module:init/1 to
%% initialize. To ensure a synchronized start-up procedure, this function
%% does not return until Module:init/1 has returned.  
%%------------------------------------------------------------------------------
start_link() ->
    gen_fsm:start_link({{{start_mode}}, ?SERVER}, ?MODULE, [], []).

%%==============================================================================
%% gen_fsm callbacks
%%==============================================================================
%%------------------------------------------------------------------------------
%% Function: init(Args) -> {ok, StateName, State} |
%%                         {ok, StateName, State, Timeout} |
%%                         ignore                              |
%%                         {stop, StopReason}                   
%% Description:Whenever a gen_fsm is started using gen_fsm:start/[3,4] or
%% gen_fsm:start_link/3,4, this function is called by the new process to 
%% initialize. 
%%------------------------------------------------------------------------------
init([]) ->
    {ok, state_name, #state{}}.

%%------------------------------------------------------------------------------
%% Function: 
%% state_name(Event, State) -> {next_state, NextStateName, NextState}|
%%                             {next_state, NextStateName, 
%%                                NextState, Timeout} |
%%                             {stop, Reason, NewState}
%% Description:There should be one instance of this function for each possible
%% state name. Whenever a gen_fsm receives an event sent using
%% gen_fsm:send_event/2, the instance of this function with the same name as
%% the current state name StateName is called to handle the event. It is also 
%% called if a timeout occurs. 
%%------------------------------------------------------------------------------
state_name(_Event, State) ->
    {next_state, state_name, State}.

%%------------------------------------------------------------------------------
%% Function:
%% state_name(Event, From, State) -> {next_state, NextStateName, NextState} |
%%                                   {next_state, NextStateName, 
%%                                     NextState, Timeout} |
%%                                   {reply, Reply, NextStateName, NextState}|
%%                                   {reply, Reply, NextStateName, 
%%                                    NextState, Timeout} |
%%                                   {stop, Reason, NewState}|
%%                                   {stop, Reason, Reply, NewState}
%% Description: There should be one instance of this function for each
%% possible state name. Whenever a gen_fsm receives an event sent using
%% gen_fsm:sync_send_event/2,3, the instance of this function with the same
%% name as the current state name StateName is called to handle the event.
%%------------------------------------------------------------------------------
state_name(_Event, _From, State) ->
    Reply = ok,
    {reply, Reply, state_name, State}.

%%------------------------------------------------------------------------------
%% Function: 
%% handle_event(Event, StateName, State) -> {next_state, NextStateName, 
%%						  NextState} |
%%                                          {next_state, NextStateName, 
%%					          NextState, Timeout} |
%%                                          {stop, Reason, NewState}
%% Description: Whenever a gen_fsm receives an event sent using
%% gen_fsm:send_all_state_event/2, this function is called to handle
%% the event.
%%------------------------------------------------------------------------------
handle_event(_Event, StateName, State) ->
    {next_state, StateName, State}.

%%------------------------------------------------------------------------------
%% Function: 
%% handle_sync_event(Event, From, StateName, 
%%                   State) -> {next_state, NextStateName, NextState} |
%%                             {next_state, NextStateName, NextState, 
%%                              Timeout} |
%%                             {reply, Reply, NextStateName, NextState}|
%%                             {reply, Reply, NextStateName, NextState, 
%%                              Timeout} |
%%                             {stop, Reason, NewState} |
%%                             {stop, Reason, Reply, NewState}
%% Description: Whenever a gen_fsm receives an event sent using
%% gen_fsm:sync_send_all_state_event/2,3, this function is called to handle
%% the event.
%%------------------------------------------------------------------------------
handle_sync_event(Event, From, StateName, State) ->
    Reply = ok,
    {reply, Reply, StateName, State}.

%%------------------------------------------------------------------------------
%% Function: 
%% handle_info(Info,StateName,State)-> {next_state, NextStateName, NextState}|
%%                                     {next_state, NextStateName, NextState, 
%%                                       Timeout} |
%%                                     {stop, Reason, NewState}
%% Description: This function is called by a gen_fsm when it receives any
%% other message than a synchronous or asynchronous event
%% (or a system message).
%%------------------------------------------------------------------------------
handle_info(_Info, StateName, State) ->
    {next_state, StateName, State}.

%%------------------------------------------------------------------------------
%% Function: terminate(Reason, StateName, State) -> void()
%% Description:This function is called by a gen_fsm when it is about
%% to terminate. It should be the opposite of Module:init/1 and do any
%% necessary cleaning up. When it returns, the gen_fsm terminates with
%% Reason. The return value is ignored.
%%------------------------------------------------------------------------------
terminate(_Reason, _StateName, _State) ->
    ok.

%%------------------------------------------------------------------------------
%% Function:
%% code_change(OldVsn, StateName, State, Extra) -> {ok, StateName, NewState}
%% Description: Convert process state when code is changed
%%------------------------------------------------------------------------------
code_change(_OldVsn, StateName, State, _Extra) ->
    {ok, StateName, State}.

%%------------------------------------------------------------------------------
%%% Internal functions
%%------------------------------------------------------------------------------

"""


SUPERVISOR_TEMPLATE = \
"""%%%-----------------------------------------------------------------------------
%%% File          : {{supervisor_name}}.erl
%%% Author        : {{author}} <{{author_email}}>
%%% Description   : Supervisor for module {{module_name}}
%%%-----------------------------------------------------------------------------
-module({{supervisor_name}}).

-behaviour(supervisor).
-define(SERVER, ?MODULE).
-define(RMS, {{restarting_mode_strategy}}).
-define(MAXR, {{max_restarts}}).
-define(MAXT, {{time_limit_on_restarts}}).

%%------------------------------------------------------------------------------
%% Exports
%%------------------------------------------------------------------------------
-export([start_link/1, start_link/0, init/1]).

%%==============================================================================
%% External functions
%%==============================================================================
%%------------------------------------------------------------------------------
%% @doc Starts the supervisor.
%% @spec start_link(StartArgs) -> {ok, pid()} | Error
%% @end
%%------------------------------------------------------------------------------
start_link() ->
    supervisor:start_link({{{start_mode}}, ?SERVER}, ?MODULE, []).

% customize start args or delete this function (from exports too!)
start_link(StartArgs) ->
    supervisor:start_link({{{start_mode}}, ?SERVER}, ?MODULE, [StartArgs]).

%%==============================================================================
%% Server functions
%%==============================================================================
%%------------------------------------------------------------------------------
%% Func: init/1
%% Returns: {ok,  {SupFlags,  [ChildSpec]}} |
%%          ignore                          |
%%          {error, Reason}
%%------------------------------------------------------------------------------
init([]) ->
    process_flag(trap_exit, true),
    io:format("~p (~p) starting...~n", [?MODULE, self()]),
    
    %% Replace "{{module_name}}" with your actual module(s)
    ChildSpecs =
    [
     {{{module_name}},
      {{{module_name}}, start_link, []},
      permanent, %% may be transient or temporary
      1000, %% time for chutdown
      worker, %% worker or supervisor
      [{{module_name}}]}
     ],
    {ok,{{?RMS, ?MAXR, ?MAXT}, ChildSpecs}}.

"""
FUNC_DOC_HL =  '%%'+'-'*78 + '\n'
SET_VAR = '"Set this var!"'

class ErlangOptionsException(Exception):
      """
      Erlang options Exception
      """
class AssignToExistingVariableException(Exception):
      """
      Exception, that raises, when code try to assing value to existing variable.
      """
      
      
